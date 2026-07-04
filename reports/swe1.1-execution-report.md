# SWE1: System Design — Web-Only Chat Architecture

## Status: ✅ Updated (Jul 2026)

## System Overview
Saratthya is a fully local AI chat system on MacBook. Web UI is the sole interface.
WhatsApp bridge removed. Opencode agents/skills remain available for tool execution.

## Architecture

```
User Browser (localhost:5050)
         │
         ▼
    Flask Web UI (dashboard.py)
         │
         ├── /api/chat → handle_message() → command_parser → run_ollama/run_agent
         ├── /api/logs → message_logger (JSONL)
         ├── /api/status → system info + bridge check
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

## Models
- `ollama/qwen2.5-coder:7b` — default, code generation
- `ollama/qwen3.5:4b` — fast explanations
- `ollama/qwen3.5:9b` — deep reasoning
- Model dropdown fetches live list from Ollama

## Personas (Command Prefixes)
| Prefix | Routes to | Backend |
|--------|-----------|---------|
| `code:` | run_ollama(qwen2.5-coder:7b) | Ollama direct |
| `explain:` | run_ollama(qwen3.5:4b) | Ollama direct |
| `reason:` | run_ollama(qwen3.5:9b) | Ollama direct |
| `shell:` | execute_shell() | subprocess |
| `file:` | execute_file_op() | Python I/O |
| `search:` | execute_search() | mdfind |
| `status` | get_status() | platform info |
| `agent:` | run_agent(name) | opencode + tool exec |

## Session Management
- Per-phone/user sessions stored in `.sessions.json`
- `session_manager.py` handles CRUD + persistence
- Clearable via `/api/chat/new`

## Key Design Decisions
1. **No WhatsApp** — Web UI only. WhatsApp can connect later via MCP server endpoint.
2. **Dual LLM backends** — Simple queries hit Ollama directly (fast, no tools). Agent tasks use opencode with tool execution.
3. **Full responses** — Web UI shows complete model output (no truncation).
4. **Local-first** — All inference on-device via Ollama. No cloud API calls.
