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
    AGENT = "agent"
    SKILL = "skill"
    UNKNOWN = "unknown"


MODEL_MAP = {
    CommandType.CODE: "ollama/qwen2.5-coder:7b",
    CommandType.EXPLAIN: "ollama/qwen3.5:4b",
    CommandType.REASON: "ollama/qwen3.5:9b",
    CommandType.SHELL: None,
    CommandType.FILE: None,
    CommandType.SEARCH: None,
    CommandType.STATUS: None,
    CommandType.AGENT: None,
    CommandType.SKILL: None,
    CommandType.UNKNOWN: None,
}

# Agent name aliases for convenience
AGENT_ALIASES = {
    "cto": "startup-cto",
    "growth": "growth-marketer",
    "founder": "solo-founder",
    "engineer": "cs-engineering-lead",
    "frontend": "cs-frontend-engineer",
    "backend": "cs-backend-engineer",
    "fullstack": "cs-fullstack-engineer",
    "product": "cs-product-manager",
    "project": "cs-project-manager",
    "qa": "cs-quality-regulatory",
    "devops": "devops-engineer",
}

PREFIX_PATTERNS = {
    CommandType.AGENT: r'^(?:--agent|agent|persona)\b',
    CommandType.CODE: r'^(?:code|write|implement|create)\b',
    CommandType.EXPLAIN: r'^(?:explain|what|how|why|describe)\b',
    CommandType.REASON: r'^(?:reason|analyze|debug|optimize)\b',
    CommandType.SHELL: r'^(?:shell|run|exec|bash|sh)\b',
    CommandType.FILE: r'^(?:file|read|write|edit|cat)\b',
    CommandType.SEARCH: r'^(?:search|find|grep|locate)\b',
    CommandType.STATUS: r'^(?:status|health|uptime|info)$',
    CommandType.SKILL: r'^(?:skill)\b',
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
