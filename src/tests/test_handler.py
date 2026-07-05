"""Tests for core/handler.py"""

import sys
sys.path.insert(0, '.')

import subprocess
from unittest.mock import patch, MagicMock
from src.core.handler import (
    _resolve_model, execute_agent, execute_shell, execute_file_op,
    execute_search, get_status, session_manager
)


def test_resolve_model_with_override():
    phone = "+test-resolve-1"
    session_manager.clear_session(phone)
    cmd_type, text, model = _resolve_model(phone, "say hello", model_override="ollama/qwen3.5:4b")
    s = session_manager.get_or_create(phone)
    assert s.current_model == "ollama/qwen3.5:4b"


def test_resolve_model_from_command():
    phone = "+test-resolve-2"
    session_manager.clear_session(phone)
    cmd_type, text, model = _resolve_model(phone, "code: write fibonacci")
    assert model == "ollama/qwen2.5-coder:7b"
    s = session_manager.get_or_create(phone)
    assert s.current_model == "ollama/qwen2.5-coder:7b"


def test_resolve_model_falls_back_to_session():
    phone = "+test-resolve-3"
    session_manager.clear_session(phone)
    session_manager.set_model(phone, "ollama/qwen3.5:4b")
    cmd_type, text, model = _resolve_model(phone, "something_random_12345")
    assert model == "ollama/qwen3.5:4b"


def test_resolve_model_override_takes_precedence():
    phone = "+test-resolve-4"
    session_manager.clear_session(phone)
    session_manager.set_model(phone, "ollama/qwen2.5-coder:7b")
    cmd_type, text, model = _resolve_model(phone, "hey", model_override="ollama/qwen3.5:9b")
    assert model == "ollama/qwen3.5:9b"


def test_execute_agent_no_parts():
    result = execute_agent("", "ollama/qwen2.5-coder:7b")
    assert "Usage" in result or "Available" in result


def test_execute_agent_no_task():
    result = execute_agent("cto:", "ollama/qwen2.5-coder:7b")
    assert "Agent" in result
    assert "selected" in result


def test_execute_agent_ollama_path():
    with patch("src.core.handler.run_ollama", return_value="ollama response") as mock_ollama:
        result = execute_agent("cto: build a roadmap", "ollama/qwen2.5-coder:7b")
        mock_ollama.assert_called_once()
        args, _ = mock_ollama.call_args
        assert "startup-cto" in args[0]
        assert result == "ollama response"


def test_execute_agent_opencode_path():
    with patch("src.core.handler.run_agent", return_value="agent response") as mock_agent:
        result = execute_agent("cto: build a roadmap", "opencode/deepseek-v4-flash-free")
        mock_agent.assert_called_once()
        assert result == "agent response"


def test_execute_shell_success():
    with patch.object(subprocess, "run") as mock_run:
        mock_run.return_value = MagicMock(stdout="hello world", stderr="", returncode=0)
        result = execute_shell("echo hello")
        assert "hello world" in result


def test_execute_shell_timeout():
    with patch.object(subprocess, "run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="echo", timeout=30)
        result = execute_shell("echo hello")
        assert "timed out" in result


def test_execute_file_op_no_parts():
    result = execute_file_op("")
    assert "Usage" in result


def test_execute_file_op_read():
    import glob as glob_mod
    with patch.object(glob_mod, "glob", return_value=["/tmp/_test_handler.txt"]):
        with patch("builtins.open", MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "test content"
            result = execute_file_op("read /tmp/_test_handler.txt")
            assert "test content" in result


def test_execute_search():
    with patch.object(subprocess, "run") as mock_run:
        mock_run.return_value = MagicMock(stdout="file1.txt\nfile2.txt", stderr="", returncode=0)
        result = execute_search("testfile")
        assert "file1.txt" in result


def test_get_status_returns_string():
    result = get_status()
    assert isinstance(result, str)
    assert "Local AI System" in result
    assert "Sessions" in result
