# SYS1 — System Requirements & Architecture

## 1. System Overview

**Project:** Saratthya — Local AI System for Web-controlled MacBook automation
**Goal:** Run a fully local AI system on MacBook controlled via a web chat UI, executing actions across the OS using opencode with skills, agents, and Ollama.
**Date:** 2026-07-05
**Status:** Active Development

## 2. Hardware & OS Specifications

| Component | Detail |
|-----------|--------|
| **Model** | MacBookPro18,3 (14-inch, 2021) |
| **SoC** | Apple M1 Pro — 10 cores (8P + 2E) |
| **RAM** | 16 GB unified memory |
| **Storage** | ~926 GB SSD |
| **OS** | macOS 26.0.1 (Build 25A362) |

## 3. Software Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python 3 | 3.11.5 | Runtime |
| Ollama | 0.30.10 | Local LLM server |
| opencode | 1.17.11 | AI coding agent |

### Local Ollama Models
| Model | Size | Use |
|-------|------|-----|
| `qwen3.5:4b` | 3.4 GB | Fast reasoning |
| `qwen3.5:9b` (latest) | 6.6 GB | Deep reasoning |
| `qwen2.5-coder:7b` | 4.7 GB | Code generation |
| `qwen3.5:4b-chat` | 3.4 GB | Chat (reserved) |

## 4. Architecture

```
User Browser (localhost:5050)
         │
         ▼
    Flask Web UI (dashboard.py)
         │
         ├── /api/chat → handle_message() → command_parser
         ├── /api/logs → message_logger (JSONL)
         ├── /api/status → system info
         ├── /api/models → Ollama model list
         └── /api/chat/new → session reset
                  │
          ┌───────┴──────────────────┐
          ▼                          ▼
   run_ollama()                run_agent()
   (Ollama HTTP API)           (opencode + tool exec)
   No tools, direct reply      Skills + MCP + tools
          │                          │
          ▼                          ▼
   Ollama (localhost:11434)    opencode agents
   qwen2.5-coder:7b            ~/.config/opencode/agents/
   qwen3.5:4b/9b               ~/.config/opencode/skills/
```

## 5. Data Flow

1. **User** opens http://localhost:5050 in browser
2. **Web UI** sends message to `/api/chat`
3. **command_parser** extracts intent and model
4. **handle_message** routes to `run_ollama` or `run_agent`
5. **Ollama** generates response (direct API or via opencode)
6. **response_formatter** formats for web display (full, no truncation)
7. **JSON response** returned to browser, rendered as chat bubble

## 6. Security

- All LLM inference is local (no cloud API calls)
- Ollama listens on `localhost:11434` only
- No credentials leave the machine
- MCP tool permissions scoped per agent

## 7. Agent Architecture

### 7.1 Agent Roles

| Persona | Model | MCP Servers | Trigger |
|---------|-------|-------------|---------|
| Architect | `qwen3.5:9b` | GitHub (projects+issues) | `agent:architect` |
| Engineer | `qwen2.5-coder:7b` | GitHub, Filesystem, Shell | `agent:engineer` |
| System | `qwen3.5:4b` | Shell, Filesystem | `agent:system` |
| DevOps | `qwen3.5:4b` | GitHub (Actions), Shell | `agent:devops` |
| Frontend | `qwen2.5-coder:7b` | Filesystem, Shell | `agent:frontend` |
| Backend | `qwen2.5-coder:7b` | Filesystem, Shell | `agent:backend` |
| Fullstack | `qwen2.5-coder:7b` | Filesystem, Shell, GitHub | `agent:fullstack` |
| QA | `qwen3.5:4b` | Shell, Filesystem | `agent:qa` |
| Product | `qwen3.5:9b` | GitHub | `agent:product` |
| Project | `qwen3.5:4b` | GitHub | `agent:project` |
| CTO | `qwen3.5:9b` | GitHub, Filesystem | `agent:cto` |
| Growth | `qwen3.5:4b` | GitHub, Shell | `agent:growth` |
| Founder | `qwen3.5:9b` | All | `agent:founder` |

### 7.2 Agent-Model Mapping (opencode.jsonc)

```jsonc
{
  "model": "opencode/deepseek-v4-flash-free",  // Default (cloud, fast)
  "small_model": "opencode/deepseek-v4-flash-free",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1",
        "headerTimeout": 180000,
        "chunkTimeout": 180000,
        "streaming": false
      },
      "models": {
        "qwen3.5:4b":         { "name": "Qwen 3.5 4B" },
        "qwen3.5:9b":         { "name": "Qwen 3.5 9B" },
        "qwen2.5-coder:7b":   { "name": "Qwen 2.5 Coder 7B" }
      }
    }
  }
}
```

## 8. Skills

| Skill | Location | Purpose |
|-------|----------|---------|
| system-admin | `~/.config/opencode/skills/` | File system, processes, brew |
| macos-control | `~/.config/opencode/skills/` | AppleScript, notifications |
| development | `~/.config/opencode/skills/` | Git, coding, testing |
| general-assistant | `~/.config/opencode/skills/` | Q&A, planning |

## 9. Project Management

- GitHub Projects (v2) for issue tracking
- GitHub MCP Server for agent access
- Board columns: Backlog → To Do → In Progress → Review → Done

## 10. Constraints

| Issue | Impact | Status |
|-------|--------|--------|
| Qwen 3.5 reasoning leak | Fixed via streaming:false | ✅ Resolved |
| 16 GB RAM limits | One ~7B model at a time | Acceptable |
| No cloud dependency | All local | ✅ By design |

## 11. Design Principles

1. **Local-first** — All processing on-device
2. **No cloud** — OpenAI/Anthropic not required
3. **Modular** — Components independently replaceable
4. **Web-only** — No external messaging dependency
5. **Dashboard as entry point** — One command to start everything
