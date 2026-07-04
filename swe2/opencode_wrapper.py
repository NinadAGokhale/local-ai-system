import subprocess
import tempfile
import shlex
from typing import Optional

DEFAULT_MODEL = "ollama/qwen2.5-coder:7b"
OPCODE_BIN = "opencode"
TIMEOUT = 120


def run_opencode(command: str, model: str = DEFAULT_MODEL) -> str:
    """Run opencode with a command and return the response text."""
    try:
        result = subprocess.run(
            [OPCODE_BIN, "run", "--model", model, command],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        output = result.stdout or result.stderr
        return strip_ansi(output.strip())
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after {} seconds".format(TIMEOUT)
    except FileNotFoundError:
        return "Error: opencode CLI not found. Is it installed?"
    except Exception as e:
        return "Error: {}".format(str(e))


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


if __name__ == "__main__":
    import sys
    cmd = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "say hello"
    print(run_opencode(cmd))
