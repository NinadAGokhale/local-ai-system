# SWE4 Execution Report: Logging Middleware + Web Dashboard

## Status: ✅ Completed

## Components

### 1. Message Logger (`swe2/message_logger.py`)
- Middleware class `MessageMiddleware` that wraps `handle_message` with automatic logging
- Logs every message to `swe2/logs/messages.jsonl` (JSONL format)
- Fields: timestamp, phone, raw_message, parsed_intent, model, response_preview, latency_ms, error
- Separate `log_requirement()` for requirement submissions
- Query functions: `get_recent_messages()`, `get_recent_requirements()`

### 2. Web Dashboard (`swe2/dashboard.py`)
- Flask app running on port 5050
- Three API endpoints: `/api/logs`, `/api/requirements`, `/api/status`
- **New Requirement form** — submits requirements that auto-create GitHub Issues via `gh issue create`
- Requirements are added to GitHub Project Board automatically
- Live system status (Ollama models count, messages logged, uptime)

### 3. Dashboard UI (`swe2/templates/dashboard.html`)
- Dark theme matching GitHub's design
- System status panel (updated every 30s)
- Requirement submission form
- Message log viewer (scrollable, shows intent badges, latency)
- Requirements history with links to GitHub issues
- Toast notifications for feedback

### 4. Integration
- `main.py` updated to use `MessageMiddleware` — all messages now pass through logger
- `whatsapp-bridge.js` updated to call `main.py` instead of direct opencode
- `requirements.txt` updated with flask dependency

## Architecture
```
WhatsApp → whatsapp-bridge.js → main.py
                                    ↓
                          MessageMiddleware (logger)
                            ↓             ↓
                      _handle_message   messages.jsonl
                            ↓
                      response → WhatsApp reply

Web Browser → dashboard.py (Flask :5050)
                  ↓
              /api/requirements → gh issue create → GitHub Issues
              /api/logs         → messages.jsonl
              /api/status       → system info
```

## Usage
```bash
# Start dashboard
pip install flask && python swe2/dashboard.py

# Open browser to http://localhost:5050
```

## Branch
`swe4-logging-dashboard` — pushed to GitHub.
