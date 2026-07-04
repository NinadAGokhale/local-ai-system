import re
from enum import Enum
from typing import Optional


class CommandType(Enum):
    CODE = "code"
    EXPLAIN = "explain"
    REASON = "reason"
    SHELL = "shell"
    FILE = "file"
    SEARCH = "search"
    STATUS = "status"
    UNKNOWN = "unknown"


MODEL_MAP = {
    CommandType.CODE: "ollama/qwen2.5-coder:7b",
    CommandType.EXPLAIN: "ollama/qwen3.5:4b",
    CommandType.REASON: "ollama/qwen3.5:9b",
    CommandType.SHELL: None,
    CommandType.FILE: None,
    CommandType.SEARCH: None,
    CommandType.STATUS: None,
}

PREFIX_PATTERNS = {
    CommandType.CODE: r'^(?:code|write|implement|create)\b',
    CommandType.EXPLAIN: r'^(?:explain|what|how|why|describe)\b',
    CommandType.REASON: r'^(?:reason|analyze|debug|optimize)\b',
    CommandType.SHELL: r'^(?:shell|run|exec|bash|sh)\b',
    CommandType.FILE: r'^(?:file|read|write|edit|cat)\b',
    CommandType.SEARCH: r'^(?:search|find|grep|locate)\b',
    CommandType.STATUS: r'^(?:status|health|uptime|info)$',
}


def parse_command(text: str) -> tuple[CommandType, str, Optional[str]]:
    """Parse a WhatsApp command and return (type, cleaned_text, model)."""
    text = text.strip()

    # Remove command prefix: "code: ", "shell: ", etc.
    for cmd_type, pattern in PREFIX_PATTERNS.items():
        match = re.match(pattern + r'[\s:]*(.*)', text, re.IGNORECASE)
        if match:
            cleaned = match.group(1).strip()
            if not cleaned:
                cleaned = text
            return cmd_type, cleaned, MODEL_MAP[cmd_type]

    return CommandType.UNKNOWN, text, MODEL_MAP[CommandType.UNKNOWN]


def get_model_for_type(cmd_type: CommandType) -> Optional[str]:
    return MODEL_MAP.get(cmd_type)
