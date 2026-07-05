"""Tests for session_manager.py"""

import sys
import os
import tempfile
sys.path.insert(0, '.')

from src.core.session_manager import Session, SessionManager


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
    assert len(d["history"]) <= 50


def test_session_context_files():
    s = Session("+1")
    s.context_files.append("/tmp/test.txt")
    d = s.to_dict()
    assert "/tmp/test.txt" in d["context_files"]


def test_session_agent_and_skill():
    s = Session("+1")
    assert s.current_agent is None
    assert s.current_skills == []
    s.current_agent = "cto"
    s.current_skills = ["content-production"]
    d = s.to_dict()
    assert d["current_agent"] == "cto"
    assert d["current_skills"] == ["content-production"]


def test_session_manager_get_or_create():
    sm = SessionManager()
    s = sm.get_or_create("+111")
    assert s.phone == "+111"
    assert sm.get_or_create("+111") is s


def test_session_manager_set_agent():
    sm = SessionManager()
    sm.set_agent("+111", "founder")
    assert sm.get_current_agent("+111") == "founder"


def test_session_manager_toggle_skill():
    sm = SessionManager()
    # Toggle on
    sm.toggle_skill("+111", "ad-creative")
    assert "ad-creative" in sm.get_current_skills("+111")
    # Toggle off
    sm.toggle_skill("+111", "ad-creative")
    assert "ad-creative" not in sm.get_current_skills("+111")


def test_session_manager_clear_agent():
    sm = SessionManager()
    sm.set_agent("+111", "cto")
    sm.set_agent("+111", None)
    assert sm.get_current_agent("+111") is None


def test_session_manager_clear_skills():
    sm = SessionManager()
    sm.toggle_skill("+111", "seo-audit")
    sm.toggle_skill("+111", "aeo")
    sm.clear_skills("+111")
    assert sm.get_current_skills("+111") == []


def test_session_manager_set_model():
    sm = SessionManager()
    sm.set_model("+111", "ollama/qwen3.5:9b")
    s = sm.get_or_create("+111")
    assert s.current_model == "ollama/qwen3.5:9b"


def test_session_new_conversation():
    s = Session("+1")
    s.history.append({"role": "user", "content": "hello"})
    s.new_conversation()
    assert s.history == []
    assert len(s.conversations) == 1


def test_session_title():
    s = Session("+1")
    assert s.get_title() == "New Chat"
    s.history.append({"role": "user", "content": "Hello world"})
    assert s.get_title() == "Hello world"
