# Saratthya — Local AI System

Agentic Market Analytics & Business Development platform. A Flask-based dashboard
that orchestrates local LLMs (Ollama) and cloud models (opencode) for multi-agent
coding, analysis, and automation.

## Architecture

```
local-ai-system/
├── src/                          # All source code
│   ├── main.py                   # Entry point (python src/main.py)
│   ├── core/                     # Core business logic
│   │   ├── config.py             # Central configuration (paths, defaults)
│   │   ├── command_parser.py     # Intent parsing (code/explain/agent/skill/...)
│   │   ├── handler.py            # Message routing & execution
│   │   ├── message_logger.py     # Logging middleware (messages.jsonl)
│   │   ├── opencode_wrapper.py   # LLM API abstraction (Ollama + opencode CLI)
│   │   ├── response_formatter.py # Output formatting & truncation
│   │   └── session_manager.py    # Session persistence (.sessions.json)
│   ├── web/                      # Flask web application
│   │   ├── dashboard.py          # API routes & server
│   │   ├── templates/            # Jinja2 templates
│   │   └── static/               # Brand assets
│   └── tests/                    # Comprehensive test suite (136 tests)
├── docs/
│   └── swe/                      # SWE workflow documentation
│       ├── SYS.md                # Orchestrator agent protocol
│       ├── SWE1.md               # Planner / Spec agent
│       ├── SWE2.md               # Implementation agent
│       ├── SWE3.md               # Code restructuring & fixes
│       └── SWE4.md               # Tests & results
├── support-doc/                  # Brand images & marketing assets
├── context_magament/             # Future feature — context management system
├── agent/                        # Agent configuration
├── logs/                         # Runtime logs (messages.jsonl, requirements.jsonl)
├── .sessions.json                # Session persistence file
└── main.py                       # Thin wrapper for backward compat
```

## Quick Start

```bash
# Install dependencies
pip install flask

# Start the dashboard
python src/main.py

# Or via the thin root wrapper
python main.py
```

Open http://localhost:5050 in your browser.

### Login

Default credentials:
- **Username**: `user`
- **Password**: `password123`

## Key Features

### Intent Parsing

The system auto-detects command types from message prefixes:

| Prefix | Type | Model |
|--------|------|-------|
| `code:` / `write:` | Code generation | `ollama/qwen2.5-coder:7b` |
| `explain:` / `what:` | Explanation | `ollama/qwen3.5:4b` |
| `reason:` / `analyze:` | Reasoning | `ollama/qwen3.5:9b` |
| `shell:` / `run:` | Shell execution | None (local) |
| `search:` / `find:` | File search | None (local) |
| `agent:` / `persona:` | Agent routing | Configurable |
| `skill:` | Skill execution | Configurable |
| `status` | System status | None (local) |

### Agent & Skill System

Select agents (@) or skills ($) from the chat UI or use text commands:

```
agent: cto: build a roadmap for Q3
skill: content-production: write a blog post about AI
```

Available agent aliases: `cto`, `growth`, `founder`, `engineer`, `frontend`,
`backend`, `fullstack`, `product`, `project`, `qa`, `devops`

### Model Routing

- **Ollama models** (`ollama/qwen*`) — direct API calls with no-tools prompt
- **Opencode cloud** (`opencode/deepseek*`) — CLI execution with full skill support
- Model auto-resolves from command prefix, session state, or UI dropdown

## Testing

```bash
# Run all tests
python -m pytest src/tests/ -v

# Run specific module
python -m pytest src/tests/test_opencode_wrapper.py -v

# Run with coverage
python -m pytest src/tests/ --cov=src
```

All 136 tests pass across 8 test modules covering parsing, routing, error
handling, API endpoints, persistence, middleware, and edge cases.

## Repository

- **GitHub**: [NinadAGokhale/local-ai-system](https://github.com/NinadAGokhale/local-ai-system)
- **Issues**: [github.com/NinadAGokhale/local-ai-system/issues](https://github.com/NinadAGokhale/local-ai-system/issues)
