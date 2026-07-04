# Local AI System — WhatsApp-Controlled MacBook Automation

Control your MacBook via WhatsApp using local LLMs, opencode, and custom automation.

## Quick Start

```bash
# 1. Start the web dashboard (single entry point)
pip install flask
python dashboard.py
# Open http://localhost:5050

# 2. Start the WhatsApp bridge (in another terminal)
cd bridge
npm install
node client.js
# Scan the QR code with WhatsApp → Linked Devices
```

## Project Structure

```
local-ai-system/
├── dashboard.py              # Web dashboard (port 5050) — single entry point
├── main.py                   # WhatsApp message handler
├── message_logger.py         # Middleware that logs all messages
├── command_parser.py         # Intent-based command parser
├── response_formatter.py     # Formats responses for WhatsApp
├── session_manager.py        # Per-user session & history
├── opencode_wrapper.py       # opencode CLI subprocess wrapper
├── whatsapp_mcp.py           # WhatsApp MCP server (for opencode agents)
├── bridge/                   # WhatsApp Web client (Node.js)
│   ├── client.js             # QR auth, receive/send messages
│   ├── package.json
│   └── power_manager.sh      # MacBook sleep prevention
├── agent/                    # opencode agent skill files
├── templates/                # Dashboard HTML templates
├── reports/                  # Execution reports for each task
├── outbox.jsonl              # Outgoing message queue (auto-created)
├── requirements.txt
└── README.md
```

## System Architecture

```
User (WhatsApp)
    │
    ▼
bridge/client.js (Node.js) ←→ QR scan links your WhatsApp
    │
    ▼
main.py → command_parser.py → opencode_wrapper.py → Ollama
    │
    ├── message_logger.py → logs/messages.jsonl
    ├── session_manager.py → .sessions.json
    └── response_formatter.py → reply to WhatsApp

Web Browser → dashboard.py (:5050)
    ├── Submit Requirement → GitHub Issue → Project Board
    ├── Message Log viewer
    └── System Status

opencode agents → whatsapp_mcp.py (MCP Server)
    ├── whatsapp_send tool
    ├── get_status tool
    ├── get_recent_messages tool
    └── execute_opencode tool
```

## Local Models

| Model | Use Case |
|-------|----------|
| `qwen2.5-coder:7b` | Primary coding tasks |
| `qwen3.5:4b` | Lightweight reasoning |
| `qwen3.5:9b` | Complex reasoning |

## Web Dashboard

```bash
python dashboard.py    # http://localhost:5050
```

- **Submit Requirement** — Creates a GitHub Issue + adds to Project Board
- **Message Log** — History of all messages with intent, model, latency
- **System Status** — Live view of Ollama models, log counts, uptime

## WhatsApp Bridge

The bridge turns your WhatsApp number into a bot:

1. `cd bridge && npm install && node client.js`
2. Scan QR code with WhatsApp (Settings → Linked Devices)
3. Send messages to your own number
4. Commands auto-detected: `code:`, `explain:`, `reason:`, `shell:`, `file:`, `search:`, `status`

## MCP Servers

| Server | Purpose |
|--------|---------|
| GitHub MCP | Issues, Projects, PRs for opencode agents |
| WhatsApp MCP | Send/receive WhatsApp + system tools for agents |

## GitHub

- **Issues/Board:** https://github.com/NinadAGokhale/local-ai-system/projects/1
- **Branch:** `dev` for development
