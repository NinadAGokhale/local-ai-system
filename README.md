# Saratthya — Local AI System

Agentic Market Analytics & Business Development platform. A Flask-based dashboard
that orchestrates local LLMs (Ollama) and cloud models (opencode) for multi-agent
coding, analysis, and automation.

## Architecture

```
local-ai-system/
├── src/
│   ├── core/                      # Core business logic
│   │   ├── config.py              # Central configuration (paths, defaults)
│   │   ├── command_parser.py      # Intent parsing (agent/skill/...)
│   │   ├── content_loader.py      # Loads agent .md / skill SKILL.md from disk
│   │   ├── handler.py             # Message routing & execution
│   │   ├── message_logger.py      # Logging middleware (messages.jsonl)
│   │   ├── opencode_wrapper.py    # LLM API abstraction (Ollama + opencode CLI)
│   │   ├── response_formatter.py  # Output formatting & truncation
│   │   └── session_manager.py     # Session persistence (.sessions.json)
│   ├── web/                       # Flask web application
│   │   ├── dashboard.py           # API routes & server (waitress on port 5002)
│   │   ├── .env.example           # Required env vars template
│   │   ├── templates/             # Jinja2 templates
│   │   └── static/                # Brand assets
│   └── tests/                     # 137 tests, all passing
├── bin/
│   ├── serve_py.py                # Waitress entry point
│   └── saratthya.sh              # Management script (start/stop/status/url/restart)
├── docs/
│   ├── swe/                       # SWE workflow documentation
│   └── ADDING-AGENTS-SKILLS.md    # Guide for adding agents & skills
├── testing/
│   └── agents-skills/             # Agent/skill audit reports & tests
├── ~/.config/opencode/
│   ├── agents/                    # 35 agent .md files (personas with tools)
│   └── skills/                    # 362 skill directories (knowledge bundles)
├── .sessions.json                 # Session persistence (auto-generated, gitignored)
└── logs/                          # Runtime logs (messages.jsonl, gitignored)
```

## Quick Start

```bash
# Install dependencies
pip install flask waitress

# Configure users (copy and edit, never commit)
cp src/web/.env.example src/web/.env
# Edit src/web/.env with real passwords

# Start the dashboard
python bin/serve_py.py

# Or use launchd (auto-restart on crash/reboot):
bin/saratthya.sh start
bin/saratthya.sh url
```

Open http://localhost:5002 in your browser.

### Public URL

The dashboard is available at **https://saratthya-agentic.nport.link** via NPort tunnel (launchd-managed, auto-restarts).

### Login

Credentials are set via environment variables in `src/web/.env`:

```
SARATTHYA_SAEE_PASSWORD=your_password
SARATTHYA_NINAD_PASSWORD=your_password
SARATTHYA_SHOUNAK_PASSWORD=your_password
SARATTHYA_SOHUM_PASSWORD=your_password
```

## Key Features

### Agent & Skill System

| Concept | What it is | Stored in |
|---------|-----------|-----------|
| **Agent** (`@`) | A persona with tool access — who executes the task | `~/.config/opencode/agents/{name}.md` |
| **Skill** (`$`) | A knowledge/instruction bundle — what methodology to follow | `~/.config/opencode/skills/{name}/SKILL.md` |

- **One agent** at a time (single persona)
- **Multiple skills** can be stacked (combined reference material)
- Agents appear in the `@` autocomplete, skills in the `$` autocomplete
- Browse all via the catalogue modal (📋 button)

Available agent aliases: `cto`, `growth`, `founder`, `engineer`, `frontend`,
`backend`, `fullstack`, `product`, `project`, `qa`, `devops`

### Prompt Construction

When an agent and skills are active, the prompt is built hierarchically:

```
[Agent: name]
{agent personality, rules, and tool definitions}

[Active Skills]
=== Skill: name ===
{methodology instructions}

[User Request]
{the actual task}
```

### Model Routing

- **Ollama models** (`ollama/qwen*`) — direct API calls, no tools
- **Opencode cloud** (`opencode/deepseek*`) — CLI execution with agent/skill context
- Model is selected per-session via the sidebar dropdown

### Multi-User Chat

- Per-user session isolation (each user sees only their conversations)
- Persistent conversation history in sidebar
- Switch between conversations without losing context
- Dark/light theme toggle (persisted in localStorage)
- Collapsible sidebar (remembers state on desktop)

## Testing

```bash
python -m pytest src/tests/ -v
```

All 137 tests pass across 8 test modules covering parsing, routing, error
handling, API endpoints, persistence, middleware, and edge cases.

## Repository

- **GitHub**: [NinadAGokhale/local-ai-system](https://github.com/NinadAGokhale/local-ai-system)
- **Issues**: [github.com/NinadAGokhale/local-ai-system/issues](https://github.com/NinadAGokhale/local-ai-system/issues)
