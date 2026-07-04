import json
import urllib.request
import urllib.error
from typing import Optional

OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "ollama/qwen2.5-coder:7b"
TIMEOUT = 120


def _strip_prefix(model: str) -> str:
    for prefix in ("ollama/", "openai/"):
        if model.startswith(prefix):
            return model[len(prefix):]
    return model


def run_opencode(command: str, model: str = DEFAULT_MODEL) -> str:
    """Run a prompt through Ollama directly and return the response text."""
    raw_model = _strip_prefix(model)
    payload = json.dumps({
        "model": raw_model,
        "prompt": command,
        "stream": False,
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


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


if __name__ == "__main__":
    import sys
    cmd = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "say hello"
    print(run_opencode(cmd))
