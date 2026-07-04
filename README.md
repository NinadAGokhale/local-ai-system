# Saratthya — Agentic Market Analytics & Business Development

Local AI system controlled via web chat UI. Uses Ollama for local LLM inference and opencode for agentic tool execution. All on-device, no cloud dependency.

## Quick Start

```bash
pip install flask
python dashboard.py
# Open http://localhost:5050
# Login: user / password123
```

## Project Structure

```
local-ai-system/
├── dashboard.py              # Flask web server (port 5050) — entry point
├── main.py                   # Core message handler (imported by dashboard)
├── opencode_wrapper.py       # Ollama direct API + opencode agent routing
├── command_parser.py         # Intent-based command parser (7 prefixes)
├── response_formatter.py     # Response formatting
├── session_manager.py        # Per-user session persistence
├── message_logger.py         # JSONL logging middleware
├── templates/
│   ├── dashboard.html        # Chat UI (ChatGPT-style)
│   └── login.html            # Login page with Saratthya branding
├── static/logo.jpeg          # Saratthya logo
├── agent/
│   ├── config-agents/        # 35 agent definitions (cs-*, startup-cto, etc.)
│   ├── skills/               # 362 skills for agentic tool execution
│   ├── sdlc-skills/          # Core skill files
│   └── opencode-config.jsonc # Reference opencode configuration
├── tests/                    # 72 unit tests
└── reports/                  # SWE execution reports
```

## Architecture

```
Browser → Login → Chat UI (localhost:5050)
                     │
                Flask API
              ┌────┴────┐
         run_ollama   run_agent
         (direct API) (opencode CLI)
              │            │
         Ollama LLMs   opencode agents
         (local)       (with skills + tools)
```

## Features

- **Login page** with username/password auth
- **Chat UI** with message bubbles, model dropdown, typing indicator
- **Model selector** — all Ollama models + opencode cloud models
- **Smart routing** — `ollama/*` → direct API (fast), `opencode/*` → opencode CLI (full tools)
- **Catalogue** modal — browse all 35 agents, 7 commands, 362 skills with search
- **7 command prefixes**: `code:`, `explain:`, `reason:`, `shell:`, `file:`, `search:`, `status`, `agent:`
- **35 agent personas** — `agent:<name>` routes through opencode with full tool execution
- **Session persistence** — chat history persisted across page reloads
- **"New Chat"** — resets session, keeps log history

## Access

| URL | Description |
|-----|-------------|
| `http://localhost:5050/` | Chat UI (after login) |
| `http://localhost:5050/login` | Login page |
| `http://localhost:5050/logout` | Logout |

Default credentials: `user` / `password123`

## Models

| Model | Type | Use Case |
|-------|------|----------|
| `ollama/qwen2.5-coder:7b` | Local | Code generation |
| `ollama/qwen3.5:4b` | Local | Fast reasoning |
| `ollama/qwen3.5:9b` | Local | Deep reasoning |
| `opencode/deepseek-v4-flash-free` | Cloud | General, full tool access |

## Agents

35 agents available. Browse full list in the Catalogue (Catalogue button in chat header). Notable agents: cs-aeo, cs-cto-advisor, cs-engineering-lead, solo-founder, startup-cto, devops-engineer, finance-lead, growth-marketer, product-manager, and 25+ cs-* persona agents.

## GitHub

- **Issues/Board:** https://github.com/NinadAGokhale/local-ai-system/projects/1
- **Branch:** `dev` for development
