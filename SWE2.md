# SWE2 — Phase 2: Web Chat Interface & End-to-End Automation

## Objective

Build a fully local chat interface (web UI) that controls MacBook via LLMs, opencode agents, and custom automation. No external dependencies — all inference on-device via Ollama.

## Architecture

```
User Browser (localhost:5050)
         │
         ▼
    Flask Web UI (dashboard.py)
         │
         ├── /api/chat → handle_message()
         ├── /api/logs → message_logger
         ├── /api/status → system info
         ├── /api/models → Ollama list
         └── /api/chat/new → session reset
                  │
          ┌───────┴────────┐
          ▼                ▼
   run_ollama()        run_agent()
   (Ollama HTTP API)   (opencode + tool exec)
          │                │
          ▼                ▼
   Ollama models     opencode agents
   (no tools)         (skills + tools)
```

## Components

### Web UI (dashboard.py + dashboard.html)
- Flask server on port 5050
- ChatGPT-style chat with message bubbles
- Model dropdown (live from Ollama API)
- "New Chat" button resets server session
- Typing indicator during processing
- System status panel

### Message Handler (main.py)
- `handle_message(phone, message)` — core router
- Routes through command_parser → run_ollama or run_agent
- Session-aware (per-user history)

### Command Parser (command_parser.py)
| Pattern | Routes to | Backend |
|---------|-----------|---------|
| `code:` | run_ollama(qwen2.5-coder:7b) | Ollama |
| `explain:` | run_ollama(qwen3.5:4b) | Ollama |
| `reason:` | run_ollama(qwen3.5:9b) | Ollama |
| `shell:` | execute_shell() | subprocess |
| `file:` | execute_file_op() | Python I/O |
| `search:` | execute_search() | mdfind |
| `status` | get_status() | platform |
| `agent:` | run_agent(name) | opencode + tools |

### Dual-Mode Backend (opencode_wrapper.py)
- `run_ollama(command, model)` — direct Ollama HTTP API, no tool execution
- `run_agent(agent_name, command)` — opencode run with agent + local tool execution

### Message Logger (message_logger.py)
- Middleware wrapping handle_message
- Logs to `logs/messages.jsonl` (JSONL format)
- Fields: timestamp, phone, message, intent, model, preview, latency, error

### Session Manager (session_manager.py)
- Per-phone/user sessions
- History with configurable max length
- JSON persistence
- clear_session() for "New Chat"

### Response Formatter (response_formatter.py)
- `format_response(text, full=True)` — no truncation for web UI
- Preserves markdown formatting
- Handles code blocks

## Files

| File | Purpose |
|------|---------|
| `dashboard.py` | Flask web server (port 5050) |
| `main.py` | Core message handler module |
| `opencode_wrapper.py` | Dual-mode: Ollama direct + opencode agent |
| `command_parser.py` | Intent-based command parser |
| `response_formatter.py` | Response formatting |
| `session_manager.py` | Per-user session persistence |
| `message_logger.py` | JSONL logging middleware |
| `templates/dashboard.html` | Chat UI template |

## Verification Checklist

- [ ] Web UI loads at http://localhost:5050
- [ ] Chat messages send and receive responses
- [ ] Model dropdown lists all Ollama models
- [ ] Model override works (takes precedence over command prefix)
- [ ] `code:` prefix routes to code model
- [ ] `explain:` prefix routes to explain model
- [ ] `reason:` prefix routes to reasoning model
- [ ] `shell:` executes terminal commands
- [ ] `file:` reads/writes files
- [ ] `search:` runs Spotlight search
- [ ] `status` shows system info
- [ ] `agent:` routes through opencode with tool execution
- [ ] "New Chat" resets session
- [ ] System status panel shows bridge/model/log info
- [ ] Session history persists across page refreshes
- [ ] Typing indicator shows during processing
- [ ] Error handling for long-running tasks
- [ ] All unit tests pass (73+)
