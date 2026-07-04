"""Tests for opencode_wrapper.py"""

import sys
from unittest.mock import patch, MagicMock
sys.path.insert(0, '.')

from opencode_wrapper import run_opencode, strip_ansi, DEFAULT_MODEL


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


@patch("opencode_wrapper.subprocess.run")
def test_run_opencode_success(mock_run):
    mock_run.return_value = MagicMock(
        stdout="\x1b[32mHello\x1b[0m",
        stderr="",
        returncode=0,
    )
    result = run_opencode("say hi")
    assert result == "Hello"
    mock_run.assert_called_once()


@patch("opencode_wrapper.subprocess.run")
def test_run_opencode_timeout(mock_run):
    import subprocess
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="opencode", timeout=120)
    result = run_opencode("slow task")
    assert "timed out" in result


@patch("opencode_wrapper.subprocess.run")
def test_run_opencode_not_found(mock_run):
    mock_run.side_effect = FileNotFoundError()
    result = run_opencode("task")
    assert "not found" in result


@patch("opencode_wrapper.subprocess.run")
def test_run_opencode_custom_model(mock_run):
    mock_run.return_value = MagicMock(stdout="result", stderr="", returncode=0)
    run_opencode("task", model="ollama/qwen3.5:9b")
    args, kwargs = mock_run.call_args
    assert "--model" in args[0]
    assert "ollama/qwen3.5:9b" in args[0]


@patch("opencode_wrapper.subprocess.run")
def test_run_opencode_default_model(mock_run):
    mock_run.return_value = MagicMock(stdout="ok", stderr="", returncode=0)
    run_opencode("task")
    args, kwargs = mock_run.call_args
    model_index = args[0].index("--model") + 1
    assert args[0][model_index] == DEFAULT_MODEL


@patch("opencode_wrapper.subprocess.run")
def test_run_opencode_uses_stderr_on_empty_stdout(mock_run):
    mock_run.return_value = MagicMock(stdout="", stderr="error msg", returncode=1)
    result = run_opencode("failing task")
    assert "error msg" in result


@patch("opencode_wrapper.subprocess.run")
def test_run_opencode_general_exception(mock_run):
    mock_run.side_effect = Exception("something broke")
    result = run_opencode("task")
    assert "something broke" in result
