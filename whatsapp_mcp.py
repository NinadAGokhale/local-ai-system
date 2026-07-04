"""WhatsApp MCP Server — exposes WhatsApp tools to opencode agents.

Run via opencode MCP config:
{
  "mcp": {
    "whatsapp": {
      "type": "remote",
      "command": ["python3", "whatsapp_mcp.py"],
      "enabled": true
    }
  }
}
"""

import json
import os
import subprocess
import time
import sys
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions

OUTBOX_FILE = os.path.join(os.path.dirname(__file__), "outbox.jsonl")
MESSAGES_LOG = os.path.join(os.path.dirname(__file__), "logs", "messages.jsonl")

server = Server("whatsapp-mcp")


def _enqueue_message(phone: str, message: str) -> str:
    os.makedirs(os.path.dirname(OUTBOX_FILE), exist_ok=True)
    entry = {
        "timestamp": time.time(),
        "phone": phone if "@c.us" in phone else f"{phone}@c.us",
        "message": message,
        "sent": False,
    }
    with open(OUTBOX_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return f"Message queued for {phone}"


def _get_recent_logs(limit: int = 10) -> list[dict]:
    if not os.path.exists(MESSAGES_LOG):
        return []
    logs = []
    with open(MESSAGES_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return list(reversed(logs))[:limit]


def _get_system_status() -> dict:
    import platform
    uptime = "N/A"
    try:
        uptime = subprocess.check_output(["uptime"]).decode().strip()
    except Exception:
        pass
    model_count = 0
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout:
            model_count = len(json.loads(result.stdout).get("models", []))
    except Exception:
        pass
    return {
        "os": f"{platform.system()} {platform.release()}",
        "host": platform.node(),
        "uptime": uptime,
        "ollama_models": model_count,
        "messages_logged": os.path.exists(MESSAGES_LOG) and sum(1 for _ in open(MESSAGES_LOG)) or 0,
    }


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="whatsapp_send",
            description="Send a WhatsApp message to a phone number. Include country code.",
            inputSchema={
                "type": "object",
                "properties": {
                    "phone": {"type": "string", "description": "Phone number with country code (e.g., +1234567890)"},
                    "message": {"type": "string", "description": "Message text to send"},
                },
                "required": ["phone", "message"],
            },
        ),
        types.Tool(
            name="get_status",
            description="Get system status including OS, uptime, Ollama models",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_recent_messages",
            description="Get recent message logs (incoming/outgoing)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "number", "description": "Number of recent messages to fetch", "default": 10},
                },
            },
        ),
        types.Tool(
            name="execute_opencode",
            description="Run an opencode task with a local model and return the response",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command/task to execute"},
                    "model": {"type": "string", "description": "Ollama model to use", "default": "ollama/qwen2.5-coder:7b"},
                },
                "required": ["command"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    arguments = arguments or {}

    if name == "whatsapp_send":
        phone = arguments.get("phone", "")
        message = arguments.get("message", "")
        result = _enqueue_message(phone, message)
        return [types.TextContent(type="text", text=result)]

    if name == "get_status":
        status = _get_system_status()
        return [types.TextContent(type="text", text=json.dumps(status, indent=2))]

    if name == "get_recent_messages":
        limit = arguments.get("limit", 10)
        logs = _get_recent_logs(limit)
        text = json.dumps(logs, indent=2) if logs else "No messages logged yet"
        return [types.TextContent(type="text", text=text)]

    if name == "execute_opencode":
        command = arguments.get("command", "")
        model = arguments.get("model", "ollama/qwen2.5-coder:7b")
        try:
            result = subprocess.run(
                ["opencode", "run", "--model", model, command],
                capture_output=True, text=True, timeout=120,
            )
            output = result.stdout or result.stderr
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            output = ansi_escape.sub('', output).strip()
            return [types.TextContent(type="text", text=output or "No output")]
        except subprocess.TimeoutExpired:
            return [types.TextContent(type="text", text="Error: Command timed out")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="whatsapp-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
