#!/usr/bin/env python3
"""WhatsApp Bot — main entry point for the Local AI System bridge."""

import sys
import os

from opencode_wrapper import run_opencode, run_agent
from command_parser import parse_command, CommandType, AGENT_ALIASES
from response_formatter import format_response
from session_manager import SessionManager
from message_logger import MessageMiddleware, log_requirement

session_manager = SessionManager()


def _handle_message(phone: str, text: str) -> str:
    """Process an incoming WhatsApp message (internal, no logging)."""
    session = session_manager.get_or_create(phone)
    session.last_command = text

    cmd_type, cleaned_text, model = parse_command(text)

    if cmd_type == CommandType.STATUS:
        return get_status()

    if cmd_type == CommandType.SHELL:
        return execute_shell(cleaned_text)

    if cmd_type == CommandType.FILE:
        return execute_file_op(cleaned_text)

    if cmd_type == CommandType.SEARCH:
        return execute_search(cleaned_text)

    if cmd_type == CommandType.AGENT:
        return execute_agent(cleaned_text)

    if model is None:
        model = session.current_model
    else:
        session_manager.set_model(phone, model)
        session.current_model = model

    result = run_opencode(cleaned_text, model=model)
    formatted = format_response(result)

    session_manager.add_to_history(phone, "user", text)
    session_manager.add_to_history(phone, "assistant", formatted)

    return formatted


# Public API: wrapped with logging middleware
handle_message = MessageMiddleware(_handle_message)


def get_status() -> str:
    import platform
    import subprocess
    uname = platform.uname()
    uptime = "N/A"
    try:
        uptime = subprocess.check_output(["uptime"]).decode().strip()
    except Exception:
        pass
    return (
        f"Local AI System\n"
        f"OS: {uname.system} {uname.release}\n"
        f"Node: {uname.node}\n"
        f"Uptime: {uptime}\n"
        f"Sessions: {len(session_manager.sessions)}"
    )


def execute_shell(command: str) -> str:
    import subprocess
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout or result.stderr
        return output[:4000] if output else "Command completed (no output)"
    except subprocess.TimeoutExpired:
        return "Shell command timed out"
    except Exception as e:
        return f"Shell error: {e}"


def execute_file_op(command: str) -> str:
    parts = command.strip().split(maxsplit=1)
    if not parts:
        return "Usage: file: <read|write|edit> <path> [content]"
    action = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""
    if action == "read":
        import glob as glob_mod
        paths = glob_mod.glob(rest)
        if not paths:
            return f"No files matching: {rest}"
        results = []
        for p in paths[:5]:
            try:
                with open(os.path.expanduser(p)) as f:
                    content = f.read()
                results.append(f"--- {p} ---\n{content[:1000]}")
            except Exception as e:
                results.append(f"--- {p} ---\nError: {e}")
        return "\n\n".join(results)
    return "File operations: read <path>"


def execute_agent(command: str) -> str:
    """Handle agent: prefix — routes to opencode agent with tool execution."""
    parts = command.strip().split(maxsplit=1)
    if not parts:
        agents = ", ".join(sorted(AGENT_ALIASES.keys()))
        return f"Usage: agent: <name> <task>\nAvailable: {agents}\nFull list: cto, growth, founder, engineer, frontend, backend, fullstack, product, project, qa, devops"
    agent_name = parts[0].lower()
    task = parts[1] if len(parts) > 1 else ""

    # Resolve alias
    agent_name = AGENT_ALIASES.get(agent_name, agent_name)

    if not task:
        return f"Agent '{agent_name}' selected. Send your task after the agent name.\nExample: agent: {agent_name}: build a todo app"

    result = run_agent(agent_name, task)
    return format_response(result)


def execute_search(command: str) -> str:
    import subprocess
    try:
        result = subprocess.run(
            ["mdfind", "-name", command],
            capture_output=True, text=True, timeout=15
        )
        lines = result.stdout.strip().split("\n")[:10]
        if not lines or lines == [""]:
            return f"No results for: {command}"
        return "Results:\n" + "\n".join(lines)
    except Exception as e:
        return f"Search error: {e}"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        phone = sys.argv[1]
        message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "status"
        print(handle_message(phone, message))
    else:
        print("Usage: python main.py <phone> <message>")
