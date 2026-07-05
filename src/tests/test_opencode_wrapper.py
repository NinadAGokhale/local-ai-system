"""Tests for opencode_wrapper.py"""

import json
import sys
from unittest.mock import patch, MagicMock
sys.path.insert(0, '.')

from src.core.opencode_wrapper import (
    run_ollama, run_agent, run_opencode, run_opencode_cli, strip_ansi,
    _strip_prefix, _execute_tool_calls, _is_opencode_error, _try_parse_tool_call,
    NO_TOOLS_PROMPT
)


def test_strip_ansi_removes_codes():
    text = "\x1b[32mHello\x1b[0m World"
    assert strip_ansi(text) == "Hello World"


def test_strip_ansi_plain_text():
    assert strip_ansi("Hello World") == "Hello World"


def test_strip_ansi_mixed():
    text = "\x1b[1mBold\x1b[0m and \x1b[31mRed\x1b[0m"
    assert strip_ansi(text) == "Bold and Red"


def test_strip_ansi_preserves_newlines():
    result = strip_ansi("text  \n  ")
    assert "text" in result
    assert "\n" in result


def test_strip_prefix_default():
    assert _strip_prefix("ollama/qwen2.5-coder:7b") == "qwen2.5-coder:7b"


def test_strip_prefix_no_prefix():
    assert _strip_prefix("qwen2.5-coder:7b") == "qwen2.5-coder:7b"


def test_strip_prefix_openai():
    assert _strip_prefix("openai/gpt-4") == "gpt-4"


@patch("src.core.opencode_wrapper.urllib.request.urlopen")
def test_run_ollama_success(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": "Hello!", "done": True}).encode()
    mock_urlopen.return_value = mock_resp

    result = run_ollama("say hi")
    assert result == "Hello!"


@patch("src.core.opencode_wrapper.urllib.request.urlopen")
def test_run_ollama_sends_system_prompt(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": "ok"}).encode()
    mock_urlopen.return_value = mock_resp

    run_ollama("my custom prompt")
    call_args = mock_urlopen.call_args
    body = json.loads(call_args[0][0].data)
    assert NO_TOOLS_PROMPT in body["system"]
    assert body["prompt"] is not None


@patch("src.core.opencode_wrapper.urllib.request.urlopen")
def test_run_ollama_custom_model(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": "ok"}).encode()
    mock_urlopen.return_value = mock_resp

    run_ollama("task", model="ollama/qwen3.5:9b")
    call_args = mock_urlopen.call_args
    body = json.loads(call_args[0][0].data)
    assert body["model"] == "qwen3.5:9b"


@patch("src.core.opencode_wrapper.urllib.request.urlopen")
def test_run_ollama_default_model(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": "ok"}).encode()
    mock_urlopen.return_value = mock_resp

    run_ollama("task")
    call_args = mock_urlopen.call_args
    body = json.loads(call_args[0][0].data)
    assert body["model"] == "qwen2.5-coder:7b"


@patch("src.core.opencode_wrapper.urllib.request.urlopen")
def test_run_ollama_stream_false(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": "ok"}).encode()
    mock_urlopen.return_value = mock_resp

    run_ollama("task")
    call_args = mock_urlopen.call_args
    body = json.loads(call_args[0][0].data)
    assert body["stream"] is False


@patch("src.core.opencode_wrapper.urllib.request.urlopen")
def test_run_ollama_http_error(mock_urlopen):
    import urllib.error
    err = urllib.error.HTTPError("http://localhost:11434/api/generate", 500, "Error", {}, None)
    err.read = lambda: b"server error"
    mock_urlopen.side_effect = err

    result = run_ollama("task")
    assert "Error: Ollama returned 500" in result


@patch("src.core.opencode_wrapper.urllib.request.urlopen")
def test_run_ollama_connection_error(mock_urlopen):
    import urllib.error
    mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
    result = run_ollama("task")
    assert "Cannot reach Ollama" in result


@patch("src.core.opencode_wrapper.urllib.request.urlopen")
def test_run_ollama_exception(mock_urlopen):
    mock_urlopen.side_effect = Exception("something broke")
    result = run_ollama("task")
    assert "something broke" in result


@patch("src.core.opencode_wrapper.subprocess.run")
def test_run_agent_success(mock_run):
    mock_run.return_value = MagicMock(stdout='{"name": "write", "arguments": {"filePath": "/tmp/test.txt", "content": "hello"}}', stderr="", returncode=0)

    result = run_agent("test-agent", "write a file")
    assert "✓ Wrote /tmp/test.txt" in result


@patch("src.core.opencode_wrapper.subprocess.run")
def test_run_agent_timeout(mock_run):
    import subprocess
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="opencode", timeout=180)

    result = run_agent("test-agent", "slow task")
    assert "timed out" in result


@patch("src.core.opencode_wrapper.subprocess.run")
def test_run_agent_not_found(mock_run):
    mock_run.side_effect = FileNotFoundError()
    result = run_agent("test-agent", "task")
    assert "not found" in result


@patch("src.core.opencode_wrapper.subprocess.run")
def test_run_agent_returns_text_if_no_tool_calls(mock_run):
    mock_run.return_value = MagicMock(stdout="Hello, I did the task!", stderr="", returncode=0)

    result = run_agent("test-agent", "say hi")
    assert result == "Hello, I did the task!"


@patch("src.core.opencode_wrapper.subprocess.run")
def test_run_agent_uses_agent_flag(mock_run):
    mock_run.return_value = MagicMock(stdout="ok", stderr="", returncode=0)

    run_agent("cs-frontend-engineer", "build a button")
    args, kwargs = mock_run.call_args
    cmd_str = " ".join(args[0])
    assert "--agent" in cmd_str
    assert "cs-frontend-engineer" in cmd_str
    assert "--auto" in cmd_str


@patch("src.core.opencode_wrapper.subprocess.run")
def test_run_agent_falls_back_on_opencode_error(mock_run):
    error_output = json.dumps({"name": "UnknownError", "data": {"message": "server error", "ref": "err_abc123"}})
    mock_run.return_value = MagicMock(stdout=error_output, stderr="", returncode=0)

    with patch("src.core.opencode_wrapper.run_opencode_cli", return_value="fallback response") as mock_fallback:
        result = run_agent("test-agent", "do task")
        mock_fallback.assert_called_once()
        assert result == "fallback response"


def test_is_opencode_error_detects_cloud_error():
    output = json.dumps({"name": "UnknownError", "data": {"message": "error", "ref": "err_123"}})
    assert _is_opencode_error(output) is True


def test_is_opencode_error_normal_text():
    assert _is_opencode_error("Hello, this is a normal response") is False


def test_is_opencode_error_empty_string():
    assert _is_opencode_error("") is False


def test_is_opencode_error_partial_json():
    assert _is_opencode_error('{"name": "UnknownError"}') is False


def test_is_opencode_error_missing_ref():
    output = json.dumps({"name": "UnknownError", "data": {"message": "error"}})
    assert _is_opencode_error(output) is False


def test_is_opencode_error_invalid_json():
    assert _is_opencode_error("not json { broken") is False


def test_try_parse_tool_call_valid():
    line = '{"name": "write", "arguments": {"filePath": "/tmp/x.txt", "content": "hi"}}'
    result = _try_parse_tool_call(line)
    assert result is not None
    assert result["name"] == "write"


def test_try_parse_tool_call_invalid():
    assert _try_parse_tool_call("not json") is None


def test_try_parse_tool_call_partial():
    assert _try_parse_tool_call('{"name": "write"}') is None


def test_execute_tool_calls_write():
    result = _execute_tool_calls(
        '{"name": "write", "arguments": {"filePath": "/tmp/_test_write.txt", "content": "test content"}}'
    )
    assert "✓ Wrote /tmp/_test_write.txt" in result


def test_execute_tool_calls_unknown():
    result = _execute_tool_calls(
        '{"name": "unknown_tool", "arguments": {}}'
    )
    assert "skipped" in result


def test_execute_tool_calls_invalid_json():
    result = _execute_tool_calls("not json at all")
    assert result == "not json at all"


def test_execute_tool_calls_empty():
    result = _execute_tool_calls("")
    assert result == ""


def test_run_opencode_is_router():
    assert run_opencode is not run_ollama
    assert callable(run_opencode)


def test_run_opencode_routes_opencode_model():
    with patch("src.core.opencode_wrapper.run_opencode_cli", return_value="cloud response") as mock_cli:
        result = run_opencode("say hi", model="opencode/deepseek-v4-flash-free")
        mock_cli.assert_called_once_with("say hi", "opencode/deepseek-v4-flash-free")
        assert result == "cloud response"


def test_run_opencode_routes_ollama_model():
    with patch("src.core.opencode_wrapper.run_ollama", return_value="ollama response") as mock_ollama:
        result = run_opencode("say hi", model="ollama/qwen2.5-coder:7b")
        mock_ollama.assert_called_once_with("say hi", "ollama/qwen2.5-coder:7b")
        assert result == "ollama response"


def test_aliases():
    assert run_ollama is not None
    assert run_agent is not None
    assert run_opencode_cli is not None
