"""Tests for session_manager.py"""

import sys
import os
import tempfile
sys.path.insert(0, '.')

from session_manager import Session


def test_session_creation():
    s = Session("+1234567890")
    assert s.phone == "+1234567890"
    assert s.history == []
    assert s.current_model == "ollama/qwen2.5-coder:7b"
    assert s.last_command is None


def test_session_to_dict():
    s = Session("+1234567890")
    s.current_model = "ollama/qwen3.5:4b"
    s.last_command = "hello"
    d = s.to_dict()
    assert d["phone"] == "+1234567890"
    assert d["current_model"] == "ollama/qwen3.5:4b"
    assert d["last_command"] == "hello"


def test_session_from_dict():
    data = {
        "phone": "+1234567890",
        "history": [{"role": "user", "content": "hi"}],
        "current_model": "ollama/qwen3.5:9b",
        "last_command": "hi",
        "context_files": [],
    }
    s = Session.from_dict(data)
    assert s.phone == "+1234567890"
    assert len(s.history) == 1
    assert s.current_model == "ollama/qwen3.5:9b"


def test_session_history_trimmed():
    s = Session("+1")
    for i in range(30):
        s.history.append({"role": "user", "content": str(i)})
    d = s.to_dict()
    assert len(d["history"]) <= 20


def test_session_context_files():
    s = Session("+1")
    s.context_files.append("/tmp/test.txt")
    d = s.to_dict()
    assert "/tmp/test.txt" in d["context_files"]
