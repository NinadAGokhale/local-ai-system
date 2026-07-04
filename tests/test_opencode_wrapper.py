"""Tests for opencode_wrapper.py"""

import json
import sys
from unittest.mock import patch, MagicMock
sys.path.insert(0, '.')

from opencode_wrapper import run_opencode, strip_ansi, DEFAULT_MODEL, _strip_prefix


def test_strip_ansi_removes_codes():
    text = "\x1b[32mHello\x1b[0m World"
    assert strip_ansi(text) == "Hello World"


def test_strip_ansi_plain_text():
    text = "Hello World"
    assert strip_ansi(text) == "Hello World"


def test_strip_ansi_mixed():
    text = "\x1b[1mBold\x1b[0m and \x1b[31mRed\x1b[0m"
    result = strip_ansi(text)
    assert result == "Bold and Red"


def test_strip_ansi_preserves_newlines():
    text = "text  \n  "
    result = strip_ansi(text)
    assert "text" in result
    assert "\n" in result


def test_strip_prefix_default():
    assert _strip_prefix("ollama/qwen2.5-coder:7b") == "qwen2.5-coder:7b"


def test_strip_prefix_no_prefix():
    assert _strip_prefix("qwen2.5-coder:7b") == "qwen2.5-coder:7b"


def test_strip_prefix_openai():
    assert _strip_prefix("openai/gpt-4") == "gpt-4"


@patch("opencode_wrapper.urllib.request.urlopen")
def test_run_opencode_success(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({
        "response": "Hello! How can I help you?",
        "done": True,
    }).encode()
    mock_urlopen.return_value = mock_resp

    result = run_opencode("say hi")
    assert result == "Hello! How can I help you?"


@patch("opencode_wrapper.urllib.request.urlopen")
def test_run_opencode_custom_model(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": "ok"}).encode()
    mock_urlopen.return_value = mock_resp

    run_opencode("task", model="ollama/qwen3.5:9b")
    call_args = mock_urlopen.call_args
    body = json.loads(call_args[0][0].data)
    assert body["model"] == "qwen3.5:9b"


@patch("opencode_wrapper.urllib.request.urlopen")
def test_run_opencode_default_model(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": "ok"}).encode()
    mock_urlopen.return_value = mock_resp

    run_opencode("task")
    call_args = mock_urlopen.call_args
    body = json.loads(call_args[0][0].data)
    assert body["model"] == "qwen2.5-coder:7b"


@patch("opencode_wrapper.urllib.request.urlopen")
def test_run_opencode_sends_prompt(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": "ok"}).encode()
    mock_urlopen.return_value = mock_resp

    run_opencode("my custom prompt")
    call_args = mock_urlopen.call_args
    body = json.loads(call_args[0][0].data)
    assert body["prompt"] == "my custom prompt"


@patch("opencode_wrapper.urllib.request.urlopen")
def test_run_opencode_stream_false(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": "ok"}).encode()
    mock_urlopen.return_value = mock_resp

    run_opencode("task")
    call_args = mock_urlopen.call_args
    body = json.loads(call_args[0][0].data)
    assert body["stream"] is False


@patch("opencode_wrapper.urllib.request.urlopen")
def test_run_opencode_http_error(mock_urlopen):
    import urllib.error
    err = urllib.error.HTTPError(
        "http://localhost:11434/api/generate", 500,
        "Internal Server Error", {}, None
    )
    err.read = lambda: b"server error"
    mock_urlopen.side_effect = err

    result = run_opencode("task")
    assert "Error: Ollama returned 500" in result


@patch("opencode_wrapper.urllib.request.urlopen")
def test_run_opencode_connection_error(mock_urlopen):
    import urllib.error
    mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

    result = run_opencode("task")
    assert "Cannot reach Ollama" in result


@patch("opencode_wrapper.urllib.request.urlopen")
def test_run_opencode_general_exception(mock_urlopen):
    mock_urlopen.side_effect = Exception("something broke")

    result = run_opencode("task")
    assert "something broke" in result


@patch("opencode_wrapper.urllib.request.urlopen")
def test_run_opencode_empty_response(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": ""}).encode()
    mock_urlopen.return_value = mock_resp

    result = run_opencode("task")
    assert result == ""
