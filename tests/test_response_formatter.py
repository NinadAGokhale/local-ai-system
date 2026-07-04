"""Tests for response_formatter.py"""

import sys
sys.path.insert(0, '.')

from response_formatter import format_response, format_code_blocks, strip_ansi


def test_empty_response():
    assert format_response("") == "No response"
    assert format_response(None) == "No response"


def test_short_response_unchanged():
    text = "Hello, this is a short response"
    assert format_response(text) == text


def test_ansi_stripped():
    text = "\x1b[32mHello\x1b[0m"
    result = format_response(text)
    assert "Hello" in result
    assert "\x1b[" not in result


def test_code_blocks_preserved():
    text = "Here is code:\n```python\nprint('hello')\n```"
    result = format_response(text)
    assert "```python" in result


def test_long_response_truncated():
    text = "A" * 5000
    result = format_response(text)
    assert len(result) <= 11000
    assert "truncated" in result or "full output" in result


def test_very_long_response_cut():
    text = "B" * 20000
    result = format_response(text)
    assert "Response too long" in result


def test_strip_ansi():
    text = "\x1b[31mRed\x1b[0m and \x1b[1mBold\x1b[0m"
    result = strip_ansi(text)
    assert result == "Red and Bold"


def test_strip_ansi_no_ansi():
    text = "Plain text"
    assert strip_ansi(text) == "Plain text"


def test_format_code_blocks():
    text = "Normal text ```code``` more text"
    result = format_code_blocks(text)
    assert "```" in result


def test_code_block_with_language():
    text = "```python\ndef foo():\n    pass\n```"
    result = format_code_blocks(text)
    assert "```python" in result


def test_mixed_content():
    result = format_response("Hello\n```\ncode block\n```\nEnd")
    assert "Hello" in result
    assert "code block" in result
