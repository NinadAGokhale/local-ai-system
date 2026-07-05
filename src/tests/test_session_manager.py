"""Tests for session_manager.py"""

import sys
import os
import tempfile
sys.path.insert(0, '.')

from src.core.session_manager import Session, SessionManager
from src.core import config as _config


def make_sm():
    """Return a SessionManager backed by a temp file so tests don't share state."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    tmp.close()
    sm = SessionManager(session_file=tmp.name)
    return sm, tmp.name


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


def test_session_title():
    s = Session("+1")
    assert s.get_title() == "New Chat"
    s.history.append({"role": "user", "content": "Hello world"})
    assert s.get_title() == "Hello world"


def _test_sm() -> SessionManager:
    sm, _ = make_sm()
    return sm


def test_session_manager_get_or_create():
    sm = _test_sm()
    s = sm.get_or_create("+111")
    assert s.phone == "+111"
    assert sm.get_or_create("+111") is s


def test_session_manager_set_agent():
    sm = _test_sm()
    sm.set_agent("+111", "founder")
    assert sm.get_current_agent("+111") == "founder"


def test_session_manager_toggle_skill():
    sm = _test_sm()
    sm.toggle_skill("+111", "ad-creative")
    assert "ad-creative" in sm.get_current_skills("+111")
    sm.toggle_skill("+111", "ad-creative")
    assert "ad-creative" not in sm.get_current_skills("+111")


def test_session_manager_clear_agent():
    sm = _test_sm()
    sm.set_agent("+111", "cto")
    sm.set_agent("+111", None)
    assert sm.get_current_agent("+111") is None


def test_session_manager_clear_skills():
    sm = _test_sm()
    sm.toggle_skill("+111", "seo-audit")
    sm.toggle_skill("+111", "aeo")
    sm.clear_skills("+111")
    assert sm.get_current_skills("+111") == []


def test_session_manager_set_model():
    sm = _test_sm()
    sm.set_model("+111", "ollama/qwen3.5:9b")
    s = sm.get_or_create("+111")
    assert s.current_model == "ollama/qwen3.5:9b"


def test_session_manager_new_conversation():
    sm = _test_sm()
    sm.add_to_history("+1", "user", "hello")
    s = sm.get_or_create("+1")
    assert s.current_conv_id == "__current__"
    sm.new_conversation("+1")
    assert s.history == []
    assert len(s.conversations) == 1
    assert s.current_conv_id == "__current__"


def test_session_manager_switch_does_not_duplicate_existing():
    """Switching between saved conversations updates in-place, no duplicates."""
    sm = _test_sm()
    sm.add_to_history("+1", "user", "chat one")
    sm.add_to_history("+1", "bot", "reply one")
    s = sm.get_or_create("+1")
    sm.new_conversation("+1")
    c1_id = s.conversations[0]["id"]
    # New conversation
    sm.add_to_history("+1", "user", "chat two")
    sm.add_to_history("+1", "bot", "reply two")
    sm.new_conversation("+1")
    assert len(s.conversations) == 2
    c2_id = s.conversations[1]["id"]
    assert c1_id != c2_id
    # Switch from c2 to c1 — c2 should be updated in-place, NOT duplicated
    sm.switch_conversation("+1", c1_id)
    assert len(s.conversations) == 2
    assert s.current_conv_id == c1_id
    # Switch back to c2 — c1 should be updated in-place, still 2 total
    sm.switch_conversation("+1", c2_id)
    assert len(s.conversations) == 2
    assert s.current_conv_id == c2_id


def test_session_manager_switch_preserves_unsaved():
    sm = _test_sm()
    sm.add_to_history("+1", "user", "hello")
    s = sm.get_or_create("+1")
    sm.new_conversation("+1")
    saved_id = s.conversations[0]["id"]
    sm.add_to_history("+1", "user", "another question")
    sm.switch_conversation("+1", saved_id)
    assert len(s.conversations) == 2
    assert s.current_conv_id == saved_id


def test_session_manager_get_conversations():
    sm = _test_sm()
    assert len(sm.get_conversations("+1")) == 0
    sm.add_to_history("+1", "user", "check")
    convs = sm.get_conversations("+1")
    assert len(convs) == 1
    assert convs[0]["id"] == "__current__"
    assert convs[0]["active"] is True
    sm.new_conversation("+1")
    convs = sm.get_conversations("+1")
    assert len(convs) == 1
    assert convs[0]["id"] != "__current__"


def test_session_manager_user_isolation():
    sm = _test_sm()
    sm.add_to_history("user-a", "user", "hello from A")
    sm.add_to_history("user-b", "user", "hello from B")
    assert len(sm.get_or_create("user-a").history) == 1
    assert len(sm.get_or_create("user-b").history) == 1
    sm.new_conversation("user-a")
    assert len(sm.get_or_create("user-a").conversations) == 1
    assert len(sm.get_or_create("user-b").conversations) == 0


def test_toggle_pin_conversation():
    sm = _test_sm()
    sm.add_to_history("+1", "user", "pin me")
    sm.new_conversation("+1")
    s = sm.get_or_create("+1")
    conv_id = s.conversations[0]["id"]
    assert s.conversations[0].get("pinned") != True

    convs = sm.toggle_pin_conversation("+1", conv_id)
    assert s.conversations[0]["pinned"] is True

    convs = sm.toggle_pin_conversation("+1", conv_id)
    assert s.conversations[0]["pinned"] is False


def test_rename_conversation():
    sm = _test_sm()
    sm.add_to_history("+1", "user", "original name")
    sm.new_conversation("+1")
    s = sm.get_or_create("+1")
    conv_id = s.conversations[0]["id"]

    convs = sm.rename_conversation("+1", conv_id, "Renamed Chat")
    assert s.conversations[0]["title"] == "Renamed Chat"

    convs = sm.rename_conversation("+1", conv_id, "")
    assert s.conversations[0]["title"] == "Untitled"

    long_title = "x" * 100
    convs = sm.rename_conversation("+1", conv_id, long_title)
    assert len(s.conversations[0]["title"]) == 80


def test_pinned_shows_in_get_conversations():
    sm = _test_sm()
    sm.add_to_history("+1", "user", "pinned chat")
    sm.new_conversation("+1")
    s = sm.get_or_create("+1")
    conv_id = s.conversations[0]["id"]
    sm.toggle_pin_conversation("+1", conv_id)

    convs = sm.get_conversations("+1")
    pinned = [c for c in convs if c["id"] == conv_id]
    assert len(pinned) == 1
    assert pinned[0]["pinned"] is True


def test_delete_conversation():
    sm = _test_sm()
    sm.add_to_history("+1", "user", "to delete")
    sm.new_conversation("+1")
    s = sm.get_or_create("+1")
    assert len(s.conversations) == 1
    conv_id = s.conversations[0]["id"]

    convs = sm.delete_conversation("+1", conv_id)
    assert len(s.conversations) == 0
    assert len(convs) == 0

def test_delete_nonexistent_conversation():
    sm = _test_sm()
    sm.add_to_history("+1", "user", "keep me")
    sm.new_conversation("+1")
    convs = sm.delete_conversation("+1", "nonexistent")
    assert len(convs) == 1
