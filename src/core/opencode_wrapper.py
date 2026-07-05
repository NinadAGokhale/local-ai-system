"""Wrapper for LLM calls — dual mode:
- run_ollama: Direct Ollama API for simple text responses (no tools)
- run_agent: opencode with --agent for full skill/tool execution
"""

import json
import os
import subprocess
import urllib.request
import urllib.error
from typing import Optional

from src.core.config import DEFAULT_MODEL

OLLAMA_HOST = "http://localhost:11434"
TIMEOUT = 180

NO_TOOLS_PROMPT = (
    "You are a helpful assistant responding via WhatsApp. "
    "Respond with text only. Do NOT use any tools, functions, or plugins. "
    "Do NOT write files or execute commands. Just give a helpful text response."
)


def _strip_prefix(model: str) -> str:
    for prefix in ("ollama/", "openai/"):
        if model.startswith(prefix):
            return model[len(prefix):]
    return model


def run_ollama(command: str, model: str = DEFAULT_MODEL) -> str:
    """Call Ollama directly with a no-tools system prompt. Returns text."""
    if not model:
        model = DEFAULT_MODEL
    raw_model = _strip_prefix(model)
    payload = json.dumps({
        "model": raw_model,
        "prompt": f"{NO_TOOLS_PROMPT}\n\nUser: {command}\n\nAssistant:",
        "stream": False,
        "system": NO_TOOLS_PROMPT,
    }).encode()

    try:
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        data = json.loads(resp.read().decode())
        return data.get("response", "").strip()
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return f"Error: Ollama returned {e.code} — {body[:200]}"
    except urllib.error.URLError as e:
        return f"Error: Cannot reach Ollama at {OLLAMA_HOST} — {e.reason}"
    except Exception as e:
        return f"Error: {e}"


def run_agent(agent_name: str, command: str) -> str:
    """Run opencode with --agent, execute tool calls locally, return summary.
    Falls back to run_opencode_cli if --agent fails.
    """
    try:
        proc = subprocess.run(
            ["opencode", "run", "--agent", agent_name, "--auto", command],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        output = proc.stdout or proc.stderr
    except subprocess.TimeoutExpired:
        return f"Error: Agent task timed out after {TIMEOUT}s"
    except FileNotFoundError:
        return "Error: opencode CLI not found"
    except Exception as e:
        return f"Error: {e}"

    if _is_opencode_error(output):
        return run_opencode_cli(f"As agent '{agent_name}', {command}")
    results = _execute_tool_calls(output)
    return results


def _is_opencode_error(output: str) -> bool:
    """Check if output is an opencode cloud API error."""
    try:
        obj = json.loads(output.strip())
        return isinstance(obj, dict) and "name" in obj and "ref" in obj.get("data", {})
    except (json.JSONDecodeError, ValueError):
        return False


def _execute_tool_calls(raw: str) -> str:
    """Parse tool call JSON from opencode output and execute locally."""
    lines = raw.strip().split("\n")
    executed = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        call = _try_parse_tool_call(line)
        if call is None:
            continue

        name = call.get("name", "")
        args = call.get("arguments", {})

        if name == "write" or name == "edit":
            path = args.get("filePath", "")
            content = args.get("content", "")
            try:
                os.makedirs(os.path.dirname(os.path.abspath(os.path.expanduser(path))) or ".", exist_ok=True)
                with open(os.path.expanduser(path), "w") as f:
                    f.write(content)
                executed.append(f"✓ Wrote {path} ({len(content)} chars)")
            except Exception as e:
                executed.append(f"✗ Failed to write {path}: {e}")

        elif name == "bash" or name == "run" or name == "shell":
            cmd = args.get("command", "") or args.get("cmd", "")
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                out = (result.stdout or result.stderr)[:500]
                executed.append(f"✓ `{cmd}` → {out.strip()}")
            except subprocess.TimeoutExpired:
                executed.append(f"✗ `{cmd}` timed out")
            except Exception as e:
                executed.append(f"✗ `{cmd}` → {e}")

        elif name == "read":
            path = args.get("filePath", "")
            try:
                with open(os.path.expanduser(path)) as f:
                    content = f.read()
                executed.append(f"✓ Read {path} ({len(content)} chars)")
            except Exception as e:
                executed.append(f"✗ Failed to read {path}: {e}")

        elif name == "webfetch":
            url = args.get("url", "")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                resp = urllib.request.urlopen(req, timeout=30)
                content = resp.read().decode()[:500]
                executed.append(f"✓ Fetched {url} ({len(content)} chars)")
            except Exception as e:
                executed.append(f"✗ Failed to fetch {url}: {e}")

        elif name == "search" or name == "grep":
            query = args.get("query", "") or args.get("pattern", "")
            try:
                result = subprocess.run(["mdfind", "-name", query], capture_output=True, text=True, timeout=15)
                out = result.stdout.strip()[:500] or "No results"
                executed.append(f"✓ Search '{query}' → {out}")
            except Exception as e:
                executed.append(f"✗ Search '{query}': {e}")

        else:
            executed.append(f"ℹ Unknown tool call: {name} — skipped")

    if executed:
        return "\n".join(executed)
    return raw


def _try_parse_tool_call(line: str) -> Optional[dict]:
    """Try to parse a line as a JSON tool call from opencode."""
    try:
        obj = json.loads(line)
        if isinstance(obj, dict) and "name" in obj and "arguments" in obj:
            return obj
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def run_opencode_cli(command: str, model: str = DEFAULT_MODEL) -> str:
    """Run opencode CLI directly with --model (for cloud models like opencode/deepseek-*)."""
    if not model:
        model = DEFAULT_MODEL
    try:
        proc = subprocess.run(
            ["opencode", "run", "--model", model, "--auto", command],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        output = proc.stdout or proc.stderr
        return strip_ansi(output.strip() or "No response")
    except subprocess.TimeoutExpired:
        return f"Error: opencode timed out after {TIMEOUT}s"
    except FileNotFoundError:
        return "Error: opencode CLI not found"
    except Exception as e:
        return f"Error: {e}"


def run_opencode(command: str, model: str = DEFAULT_MODEL) -> str:
    """Route to appropriate backend based on model prefix.
    ollama/* -> direct Ollama API (fast, no tools)
    opencode/* -> opencode CLI (skills + tools available)
    """
    if not model:
        model = DEFAULT_MODEL
    if model.startswith("opencode/"):
        return run_opencode_cli(command, model)
    return run_ollama(command, model)


def strip_ansi(text: str) -> str:
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
