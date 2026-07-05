"""Middleware logger — intercepts and logs all messages and responses."""

import json
import os
import time
from datetime import datetime
from typing import Optional

from src.core.config import LOG_DIR

MESSAGES_LOG = os.path.join(LOG_DIR, "messages.jsonl")
REQUIREMENTS_LOG = os.path.join(LOG_DIR, "requirements.jsonl")


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def log_message(
    phone: str,
    raw_message: str,
    parsed_intent: str,
    model: Optional[str],
    response: str,
    latency_ms: float,
    error: Optional[str] = None,
):
    ensure_log_dir()
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "phone": phone,
        "raw_message": raw_message,
        "parsed_intent": parsed_intent,
        "model": model,
        "response_preview": response[:5000],
        "response_length": len(response),
        "latency_ms": round(latency_ms, 2),
        "error": error,
    }
    with open(MESSAGES_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def log_requirement(
    phone: str,
    requirement_text: str,
    issue_url: Optional[str] = None,
    status: str = "created",
):
    ensure_log_dir()
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "phone": phone,
        "requirement": requirement_text,
        "issue_url": issue_url,
        "status": status,
    }
    with open(REQUIREMENTS_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_recent_messages(limit: int = 50, phone: Optional[str] = None):
    """Get recent message logs, newest first."""
    ensure_log_dir()
    if not os.path.exists(MESSAGES_LOG):
        return []
    messages = []
    with open(MESSAGES_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    msg = json.loads(line)
                    if phone is None or msg.get("phone") == phone:
                        messages.append(msg)
                except json.JSONDecodeError:
                    continue
    return list(reversed(messages))[:limit]


def get_recent_requirements(limit: int = 20):
    ensure_log_dir()
    if not os.path.exists(REQUIREMENTS_LOG):
        return []
    reqs = []
    with open(REQUIREMENTS_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    reqs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return list(reversed(reqs))[:limit]


class MessageMiddleware:
    """Decorator-style middleware that wraps message handling with logging."""

    def __init__(self, handler_func):
        self.handler = handler_func

    def __call__(self, phone: str, text: str, **kwargs):
        from src.core import command_parser
        start = time.time()
        error = None
        result = ""

        cmd_type, cleaned, model = command_parser.parse_command(text)

        model = kwargs.get("model_override") or model

        try:
            result = self.handler(phone, text, **kwargs)
        except Exception as e:
            error = str(e)
            result = f"Error: {error}"

        latency = (time.time() - start) * 1000

        log_message(
            phone=phone,
            raw_message=text,
            parsed_intent=cmd_type.value if cmd_type else "unknown",
            model=model,
            response=result,
            latency_ms=latency,
            error=error,
        )

        return result
