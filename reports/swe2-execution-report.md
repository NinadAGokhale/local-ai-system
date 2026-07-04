# SWE2: Requirements — Web-Only Chat Interface

## Status: ✅ Updated (Jul 2026)

## Files

| File | Purpose |
|------|---------|
| `dashboard.py` | Flask web server (port 5050) — sole entry point |
| `main.py` | Core message handler module (imported by dashboard) |
| `opencode_wrapper.py` | Dual-mode: Ollama direct + opencode agent runner |
| `command_parser.py` | Intent-based command parser with prefix routing |
| `response_formatter.py` | Response formatting (supports full mode for web) |
| `session_manager.py` | Per-user session persistence |
| `message_logger.py` | JSONL logging middleware |
| `templates/dashboard.html` | Full chat UI (ChatGPT-style) |
| `whatsapp_mcp.py` | [REMOVED] WhatsApp MCP server |
| `bridge/` | [REMOVED] WhatsApp Web client + Node.js bridge |

## Core Requirements

### 1. Web Chat Interface (REQ-WEB-01)
- ChatGPT-style chat UI at `http://localhost:5050`
- Message bubbles with user/saratthya distinction
- Full response display (no truncation)
- Auto-resize textarea input
- Enter to send, Shift+Enter for newline
- Typing indicator during processing

### 2. Model Selection (REQ-MOD-01)
- Dropdown listing all local Ollama models
- Model override takes precedence over command-parsed model
- Fetches live model list from Ollama API

### 3. Command Prefixes (REQ-CMD-01)
- `code:` → code generation (no tools)
- `explain:` → explanations (no tools)
- `reason:` → deep reasoning (no tools)
- `shell:` → Mac terminal commands
- `file:` → file read/write
- `search:` → Spotlight file search
- `status` → system info
- `agent:` → opencode agent with tool execution

### 4. Session Management (REQ-SES-01)
- Per-user conversation history
- Persistent across server restarts (JSON file)
- "New Chat" button resets session

### 5. Agent/Skill Integration (REQ-AGT-01)
- `agent:` prefix routes through opencode with selected agent
- Agent definitions in `~/.config/opencode/agents/`
- Skills in `~/.config/opencode/skills/`
- Tool calls (write, bash, read, webfetch, search) executed locally

### 6. Logging (REQ-LOG-01)
- All messages logged to `logs/messages.jsonl`
- 5000-char response preview stored
- Latency tracking per message

### 7. System Status (REQ-STA-01)
- Bridge online/offline indicator
- Ollama model count
- Messages processed count
- Session count
- Uptime display

## Removed Requirements
- WhatsApp bridge (`bridge/`) — removed
- WhatsApp MCP server (`whatsapp_mcp.py`) — removed
- QR code auth — removed
- Node.js runtime dependency — removed

## Startup
```bash
cd ~/Desktop/local-ai-system && python dashboard.py
# Open http://localhost:5050
```
