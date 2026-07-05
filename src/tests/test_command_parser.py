"""Tests for command_parser.py"""

import sys
sys.path.insert(0, '.')

from src.core.command_parser import parse_command, CommandType, get_model_for_type, AGENT_ALIASES, MODEL_MAP, PREFIX_PATTERNS


def test_parse_code_command():
    cmd_type, text, model = parse_command("code: write fibonacci in python")
    assert cmd_type == CommandType.CODE
    assert model == "ollama/qwen2.5-coder:7b"
    assert "write fibonacci in python" in text


def test_parse_explain_command():
    cmd_type, text, model = parse_command("explain: what is machine learning")
    assert cmd_type == CommandType.EXPLAIN
    assert model == "ollama/qwen3.5:4b"


def test_parse_reason_command():
    cmd_type, text, model = parse_command("reason: why is my code slow")
    assert cmd_type == CommandType.REASON
    assert model == "ollama/qwen3.5:9b"


def test_parse_shell_command():
    cmd_type, text, model = parse_command("shell: ls -la")
    assert cmd_type == CommandType.SHELL
    assert model is None


def test_parse_file_command():
    cmd_type, text, model = parse_command("file: read /tmp/test.txt")
    assert cmd_type == CommandType.FILE
    assert model is None


def test_parse_search_command():
    cmd_type, text, model = parse_command("search: myfile.txt")
    assert cmd_type == CommandType.SEARCH
    assert model is None


def test_parse_status_command():
    cmd_type, text, model = parse_command("status")
    assert cmd_type == CommandType.STATUS
    assert model is None


def test_parse_unknown_command():
    cmd_type, text, model = parse_command("hello how are you")
    assert cmd_type == CommandType.UNKNOWN
    assert model is None


def test_parse_code_without_colon():
    cmd_type, text, model = parse_command("code write hello world")
    assert cmd_type == CommandType.CODE


def test_parse_explain_without_colon():
    cmd_type, text, model = parse_command("explain gravity")
    assert cmd_type == CommandType.EXPLAIN


def test_parse_empty_string():
    cmd_type, text, model = parse_command("")
    assert cmd_type == CommandType.UNKNOWN


def test_parse_case_insensitive():
    cmd_type, text, model = parse_command("CODE: write python")
    assert cmd_type == CommandType.CODE


def test_parse_write_synonym():
    cmd_type, text, model = parse_command("write a script to backup files")
    assert cmd_type == CommandType.CODE


def test_parse_implement_synonym():
    cmd_type, text, model = parse_command("implement a queue in go")
    assert cmd_type == CommandType.CODE


def test_parse_create_synonym():
    cmd_type, text, model = parse_command("create a new project structure")
    assert cmd_type == CommandType.CODE


def test_parse_agent_command():
    cmd_type, text, model = parse_command("agent: cto: build a roadmap")
    assert cmd_type == CommandType.AGENT
    assert model is None


def test_parse_skill_command():
    cmd_type, text, model = parse_command("skill: content-production: write a post")
    assert cmd_type == CommandType.SKILL
    assert model is None


def test_parse_skill_without_colon():
    cmd_type, text, model = parse_command("skill content-production write a post")
    assert cmd_type == CommandType.SKILL


def test_parse_skill_prefix_in_patterns():
    assert CommandType.SKILL in PREFIX_PATTERNS


def test_parse_skill_in_model_map():
    assert CommandType.SKILL in MODEL_MAP
    assert MODEL_MAP[CommandType.SKILL] is None


def test_agent_aliases_include_shorts():
    assert "cto" in AGENT_ALIASES
    assert AGENT_ALIASES["cto"] == "startup-cto"
    assert "backend" in AGENT_ALIASES
    assert AGENT_ALIASES["backend"] == "cs-backend-engineer"


def test_get_model_for_type():
    assert get_model_for_type(CommandType.CODE) == "ollama/qwen2.5-coder:7b"
    assert get_model_for_type(CommandType.UNKNOWN) is None


def test_get_model_for_type_none():
    assert get_model_for_type(CommandType.STATUS) is None
    assert get_model_for_type(CommandType.SHELL) is None
