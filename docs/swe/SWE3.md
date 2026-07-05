# SWE3 — Code Restructuring & Bug Fixes

## Overview

Complete restructuring of the Saratthya codebase from a flat layout to a modular
`src/` directory, along with fixes for the @/$ autocomplete bug, mode selection
error, and skill prefix support.

## Code Restructuring

### Before (flat layout)

```
command_parser.py
dashboard.py
main.py
message_logger.py
opencode_wrapper.py
response_formatter.py
session_manager.py
templates/ (dashboard.html, login.html)
static/ (logo.jpeg)
tests/ (6 test files)
```

### After (modular src/ layout)

```
src/
├── main.py                     # Entry point (python src/main.py)
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py               # NEW — central config (paths, constants)
│   ├── command_parser.py
│   ├── handler.py              # Was root main.py (message handler)
│   ├── message_logger.py
│   ├── opencode_wrapper.py
│   ├── response_formatter.py
│   └── session_manager.py
├── web/
│   ├── __init__.py
│   ├── dashboard.py            # Flask web app
│   ├── templates/
│   │   ├── dashboard.html
│   │   └── login.html
│   └── static/
│       └── logo.jpeg
└── tests/
    ├── __init__.py
    ├── test_command_parser.py   # Updated — +skill prefix tests
    ├── test_config.py           # NEW — config paths
    ├── test_dashboard.py        # Updated — +agent/skill API tests
    ├── test_handler.py          # NEW — _resolve_model, execute_agent tests
    ├── test_message_logger.py
    ├── test_opencode_wrapper.py # Updated — +_is_opencode_error tests
    ├── test_response_formatter.py
    └── test_session_manager.py  # Updated — +agent/skill state tests
```

Root-level thin wrappers (`main.py`, `dashboard.py`, `command_parser.py`, etc.)
re-export from `src/` for backward compatibility.

### Key architectural changes

1. **Central config** (`src/core/config.py`): All file paths (SESSION_FILE,
   LOG_DIR) derive from PROJECT_ROOT instead of `__file__`, making paths
   consistent regardless of CWD.

2. **Message handler** moved to `src/core/handler.py` (was root `main.py`).
   The root `main.py` now only serves as the entry point thunk.

3. **Flask app** (`src/web/dashboard.py`): Imports from `src.core.*` instead
   of root-level modules.

## Bug Fixes Applied

### Bug 1: @/$ autocomplete not working
- **Root cause**: `before.endsWith('@')` detection was fragile; inline `onclick`
  handlers broke on re-render; @/$ mentions only stripped at start of text.
- **Fix**: `e.data` from InputEvent for detection; event delegation via
  `ac-list` listener for click handlers; global `replace(/@(\S+)/g, ...)` in
  `sendMessage()`.

### Bug 2: "response body failure" when selecting a mode
- **Root cause**: `execute_agent()` ignored user's model selection; opencode
  `--agent` flag crashes at the cloud API level with `UnknownError`.
- **Fix**: `_is_opencode_error()` detection + fallback to `run_opencode_cli`;
  `execute_agent()` now routes Ollama models to direct API with agent context.

### Bug 3: Skill prefix not recognized
- **Root cause**: `skill:` prefix missing from `PREFIX_PATTERNS` in
  `command_parser.py`; skill context silently dropped when agent was active
  in `dashboard.py`.
- **Fix**: Added `SKILL` CommandType + `skill:` pattern; removed `if not
  s.current_agent:` guard so both agent and skill context are prepended.

## New Functions Added

| Function | File | Purpose |
|----------|------|---------|
| `_is_opencode_error()` | `opencode_wrapper.py` | Detects cloud API error JSON |
| `_resolve_model()` | `handler.py` | Resolves model from override/command/session |
| `src/core/config.py` | `config.py` | Central path constants |

## Files Created

| File | Type |
|------|------|
| `src/__init__.py` | Package init |
| `src/core/__init__.py` | Package init |
| `src/web/__init__.py` | Package init |
| `src/tests/__init__.py` | Package init |
| `src/core/config.py` | Configuration |
| `src/core/handler.py` | Message handler (moved from root main.py) |
| `src/main.py` | Entry point |
| `docs/swe/SWE3.md` | This file |
| `docs/swe/SWE4.md` | Tests documentation |
| `support-doc/` | Brand assets |

## Files Modified

| File | Change |
|------|--------|
| `src/core/command_parser.py` | Added SKILL CommandType, PREFIX_PATTERNS, MODEL_MAP entries |
| `src/core/opencode_wrapper.py` | Added `_is_opencode_error()`, fallback logic |
| `src/web/dashboard.py` | Fixed skill context prepending (removed agent guard) |
| `src/web/templates/dashboard.html` | Fixed @ detection, event delegation, global @ strip |

## GitHub Issues

- #32: SWE3 — Restructure code into src/ directory
- #33: SWE3 — Create src/main.py as system-wide entry point
- #34: SWE4 — Create comprehensive unit tests for all fixes
