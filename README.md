# Saratthya — Local AI System (Web-controlled MacBook Automation)

Control your MacBook via a local web chat UI using local LLMs, opencode, and custom automation.

## Quick Start

```bash
# Start the web dashboard (single entry point)
pip install flask
python dashboard.py
# Open http://localhost:5050
```

## Project Structure

```
local-ai-system/
├── dashboard.py              # Flask web server (port 5050) — entry point
├── main.py                   # Core message handler (imported by dashboard)
├── opencode_wrapper.py       # Dual-mode: Ollama direct + opencode agent
├── command_parser.py         # Intent-based command parser
├── response_formatter.py     # Formats responses (full mode for web UI)
├── session_manager.py        # Per-user session & history
├── message_logger.py         # Middleware that logs all messages
├── templates/dashboard.html  # Chat UI (ChatGPT-style)
├── agent/                    # opencode agent/skill definitions
│   ├── sdlc-skills/          # Skill instruction files
│   └── *-agent.md            # Agent persona definitions
├── tests/                    # Unit tests (73+ passing)
├── reports/                  # SWE execution reports
└── README.md
```

## System Architecture

```
User Browser (localhost:5050)
         │
         ▼
    Flask Web UI (dashboard.py)
         │
         ├── /api/chat → handle_message() → command_parser → run_ollama/run_agent
         ├── /api/logs → message_logger (JSONL)
         ├── /api/status → system info
         ├── /api/models → Ollama model list
         └── /api/chat/new → session reset
                  │
          ┌───────┴────────┐
          ▼                ▼
   run_ollama()        run_agent()
   (Ollama HTTP API)   (opencode + tool execution)
          │                │
          ▼                ▼
   Ollama models     opencode agents
   (local, no tools)  (with skills + tools)
```

## Local Models

| Model | Use Case |
|-------|----------|
| `qwen2.5-coder:7b` | Primary coding tasks |
| `qwen3.5:4b` | Lightweight reasoning |
| `qwen3.5:9b` | Complex reasoning |

## Chat Interface

```bash
python dashboard.py    # http://localhost:5050
```

- **ChatGPT-style UI** with message bubbles, model dropdown, typing indicator
- **Model selector** — choose any local Ollama model
- **Command prefixes** — `code:`, `explain:`, `reason:`, `shell:`, `file:`, `search:`, `status`, `agent:`
- **Agent persona routing** — `agent:<name>` runs through opencode with specified agent + tool execution
- **New Chat** — resets session
- **Message Log** — history with intent, model, latency

## Agent Personas

| Prefix | Agent | Backend |
|--------|-------|---------|
| `agent:engineer` | Engineer | opencode + tools |
| `agent:architect` | Architect | opencode + tools |
| `agent:frontend` | Frontend | opencode + tools |
| `agent:backend` | Backend | opencode + tools |
| `agent:devops` | DevOps | opencode + tools |
| `agent:qa` | QA | opencode + tools |
| `agent:product` | Product | opencode + tools |
| `agent:project` | Project | opencode + tools |
| `agent:cto` | CTO | opencode + tools |
| `agent:growth` | Growth | opencode + tools |
| `agent:founder` | Founder | opencode + tools |
| `agent:fullstack` | Fullstack | opencode + tools |

## GitHub

- **Issues/Board:** https://github.com/NinadAGokhale/local-ai-system/projects/1
- **Branch:** `dev` for development
