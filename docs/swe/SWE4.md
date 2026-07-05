# SWE4 — Unit Tests & Test Results

## Overview

Comprehensive unit test suite covering all core modules, including new tests
for the bug fixes and restructuring. All tests pass (136/136).

## Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `test_command_parser.py` | 23 | All CommandTypes, skill prefix, agents, edge cases |
| `test_config.py` | 7 | PROJECT_ROOT, SESSION_FILE, LOG_DIR, DEFAULT_MODEL |
| `test_dashboard.py` | 18 | Flask API endpoints, login, agent/skill CRUD, chat |
| `test_handler.py` | 16 | `_resolve_model`, `execute_agent`, shell, file, search, status |
| `test_message_logger.py` | 9 | Log creation, retrieval, filtering, ordering |
| `test_opencode_wrapper.py` | 31 | `_is_opencode_error`, tool calls, routing, fallback, edge cases |
| `test_response_formatter.py` | 11 | Truncation, ANSI strip, code blocks, full mode |
| `test_session_manager.py` | 13 | Sessions, agent/skill state, conversations, persistence |
| **Total** | **136** | |

## New Tests for Bug Fixes

### `_is_opencode_error` (6 tests)

| Test | Scenario |
|------|----------|
| `test_is_opencode_error_detects_cloud_error` | Full error JSON with name + ref |
| `test_is_opencode_error_normal_text` | Plain text response |
| `test_is_opencode_error_empty_string` | Empty string |
| `test_is_opencode_error_partial_json` | Missing "ref" in data |
| `test_is_opencode_error_missing_ref` | Has name but no ref in data |
| `test_is_opencode_error_invalid_json` | Malformed JSON |

### `execute_agent` model routing (4 tests)

| Test | Scenario |
|------|----------|
| `test_execute_agent_no_parts` | Empty command |
| `test_execute_agent_no_task` | Agent selected but no task |
| `test_execute_agent_ollama_path` | Ollama model -> direct API |
| `test_execute_agent_opencode_path` | Opencode model -> run_agent |

### `_resolve_model` (4 tests)

| Test | Scenario |
|------|----------|
| `test_resolve_model_with_override` | Model override parameter |
| `test_resolve_model_from_command` | Model from command prefix |
| `test_resolve_model_falls_back_to_session` | Falls back to session model |
| `test_resolve_model_override_takes_precedence` | Override > command > session |

### `run_opencode` routing (2 tests)

| Test | Scenario |
|------|----------|
| `test_run_opencode_routes_opencode_model` | Routes to CLI |
| `test_run_opencode_routes_ollama_model` | Routes to direct API |

### Skill prefix parsing (6 tests)

| Test | Scenario |
|------|----------|
| `test_parse_skill_command` | `skill: name: task` |
| `test_parse_skill_without_colon` | `skill name task` |
| `test_parse_skill_prefix_in_patterns` | SKILL in PREFIX_PATTERNS |
| `test_parse_skill_in_model_map` | SKILL in MODEL_MAP |

## Test Results

```
============================= 136 passed in 0.26s ==============================
```

### Command to run

```bash
cd /path/to/local-ai-system
python -m pytest src/tests/ -v
```

### Old test compat (deprecated)

The old tests at root `tests/` still work as thin wrappers:

```bash
python -m pytest tests/ -v   # Falls through to src/tests/
```

## Test Quality Metrics

- **Total tests**: 136
- **Passed**: 136
- **Failed**: 0
- **Test modules**: 8
- **Coverage areas**: Parsing, routing, error handling, edge cases, API,
  persistence, middleware, formatting
