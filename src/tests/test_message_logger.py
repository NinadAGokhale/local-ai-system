"""Tests for message_logger.py"""

import sys
import os
import tempfile
import json
sys.path.insert(0, '.')

import src.core.message_logger as ml


def test_log_message_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        ml.LOG_DIR = tmp
        ml.MESSAGES_LOG = os.path.join(tmp, "messages.jsonl")
        ml.log_message("+111", "hello", "unknown", None, "hi", 100.0)
        assert os.path.exists(ml.MESSAGES_LOG)
        with open(ml.MESSAGES_LOG) as f:
            data = json.loads(f.readline())
        assert data["phone"] == "+111"
        assert data["raw_message"] == "hello"
        assert data["latency_ms"] == 100.0


def test_log_message_with_model():
    with tempfile.TemporaryDirectory() as tmp:
        ml.LOG_DIR = tmp
        ml.MESSAGES_LOG = os.path.join(tmp, "messages.jsonl")
        ml.log_message("+222", "code: fib", "code", "ollama/qwen2.5-coder:7b", "def fib(): ...", 5000.5)
        with open(ml.MESSAGES_LOG) as f:
            data = json.loads(f.readline())
        assert data["model"] == "ollama/qwen2.5-coder:7b"
        assert data["parsed_intent"] == "code"


def test_log_message_with_error():
    with tempfile.TemporaryDirectory() as tmp:
        ml.LOG_DIR = tmp
        ml.MESSAGES_LOG = os.path.join(tmp, "messages.jsonl")
        ml.log_message("+333", "bad cmd", "unknown", None, "", 50.0, error="Timeout")
        with open(ml.MESSAGES_LOG) as f:
            data = json.loads(f.readline())
        assert data["error"] == "Timeout"


def test_get_recent_messages():
    with tempfile.TemporaryDirectory() as tmp:
        ml.LOG_DIR = tmp
        ml.MESSAGES_LOG = os.path.join(tmp, "messages.jsonl")
        ml.log_message("+1", "msg1", "code", "m1", "r1", 10.0)
        ml.log_message("+2", "msg2", "shell", "m2", "r2", 20.0)
        ml.log_message("+1", "msg3", "status", None, "r3", 5.0)
        msgs = ml.get_recent_messages(limit=10)
        assert len(msgs) == 3
        assert msgs[0]["raw_message"] == "msg3"


def test_get_recent_messages_with_phone_filter():
    with tempfile.TemporaryDirectory() as tmp:
        ml.LOG_DIR = tmp
        ml.MESSAGES_LOG = os.path.join(tmp, "messages.jsonl")
        ml.log_message("+1", "a", "code", None, "x", 1.0)
        ml.log_message("+2", "b", "shell", None, "y", 2.0)
        msgs = ml.get_recent_messages(limit=10, phone="+2")
        assert len(msgs) == 1
        assert msgs[0]["phone"] == "+2"


def test_get_recent_messages_empty():
    with tempfile.TemporaryDirectory() as tmp:
        ml.LOG_DIR = tmp
        ml.MESSAGES_LOG = os.path.join(tmp, "messages.jsonl")
        msgs = ml.get_recent_messages()
        assert msgs == []


def test_log_requirement():
    with tempfile.TemporaryDirectory() as tmp:
        ml.LOG_DIR = tmp
        ml.REQUIREMENTS_LOG = os.path.join(tmp, "requirements.jsonl")
        ml.log_requirement("+1", "build a calculator", "https://github.com/issue/1")
        with open(ml.REQUIREMENTS_LOG) as f:
            data = json.loads(f.readline())
        assert data["requirement"] == "build a calculator"
        assert data["issue_url"] == "https://github.com/issue/1"


def test_multiple_logs_order():
    with tempfile.TemporaryDirectory() as tmp:
        ml.LOG_DIR = tmp
        ml.MESSAGES_LOG = os.path.join(tmp, "messages.jsonl")
        ml.log_message("+1", "first", "code", None, "r1", 1.0)
        ml.log_message("+1", "second", "explain", None, "r2", 2.0)
        ml.log_message("+1", "third", "reason", None, "r3", 3.0)
        msgs = ml.get_recent_messages(limit=2)
        assert len(msgs) == 2
        assert msgs[0]["raw_message"] == "third"
        assert msgs[1]["raw_message"] == "second"


def test_get_recent_requirements_empty():
    with tempfile.TemporaryDirectory() as tmp:
        ml.LOG_DIR = tmp
        ml.REQUIREMENTS_LOG = os.path.join(tmp, "requirements.jsonl")
        reqs = ml.get_recent_requirements()
        assert reqs == []
