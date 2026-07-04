# SYS2 — Technical Design & Implementation Plan

## 1. Implementation Phases

| Phase | Name | Duration | Dependencies |
|-------|------|----------|--------------|
| SWE1 | Local Model Setup & opencode Integration | 1-2 days | — |
| SWE2 | Web Chat Interface & Automation | 3-5 days | SWE1 |
| SWE3 | Agent Architecture & Project Automation | 2-3 days | SWE1 |
| SWE4 | Logging + Dashboard Finalization | 1-2 days | SWE2 |

## 2. Model Analysis

| Criteria | qwen3.5:4b | qwen3.5:9b | qwen2.5-coder:7b |
|----------|------------|------------|-------------------|
| **Size** | 3.4 GB | 6.6 GB | 4.7 GB |
| **RAM usage** | ~4 GB | ~8 GB | ~6 GB |
| **Speed** | ~10 tok/s | ~6 tok/s | ~12 tok/s |
| **Code quality** | Good | Very Good | Excellent |
| **General reasoning** | Excellent | Excellent | Moderate |

### Default: qwen2.5-coder:7b (no reasoning leak, best code)

## 3. Component Architecture

### 3.1 opencode Configuration
- Provider-level `streaming: false` for Qwen 3.5 compatibility
- Models: qwen3.5:4b, qwen3.5:9b, qwen2.5-coder:7b
- MCP: GitHub (remote) — Issues, Projects, PRs

### 3.2 Skills
- `system-admin.md` — File system, process management
- `macos-control.md` — macOS-specific actions (AppleScript, automation)
- `development.md` — Git, coding, project management
- `general-assistant.md` — General Q&A, task planning

### 3.3 Agents (31 at ~/.config/opencode/agents/)
- Built-in agents + custom persona agents (cs-*, founder, cto, etc.)
- All accessible via `agent:<name>` prefix in web UI

## 4. Web Chat Interface

### 4.1 Architecture
```
Flask (dashboard.py:5050)
  → /api/chat → handle_message → command_parser + run_ollama/run_agent
  → /api/status → system info
  → /api/models → Ollama model list
  → /api/logs → message_logger
```

### 4.2 Command Routing
| Prefix | Backend | Model |
|--------|---------|-------|
| `code:` | Ollama direct | qwen2.5-coder:7b |
| `explain:` | Ollama direct | qwen3.5:4b |
| `reason:` | Ollama direct | qwen3.5:9b |
| `shell:` | subprocess | None |
| `file:` | Python I/O | None |
| `search:` | mdfind | None |
| `status` | platform | None |
| `agent:` | opencode + tools | Agent-configured |

### 4.3 Session Management
- Per-user sessions with JSON persistence
- Configurable history length
- "New Chat" resets session

## 5. GitHub Project Board Schema

```
Project: "Local AI System" (GitHub Projects v2)
├── Status: Backlog → To Do → In Progress → Review → Done
├── Phase: SWE1 / SWE2 / SWE3 / SWE4
├── Persona: Architect / Engineer / System / DevOps / Frontend / etc.
├── Priority: P0 / P1 / P2
└── Agent: (text — assigned agent name)
```

## 6. Credentials

| Service | What | Status |
|---------|------|--------|
| GitHub | Free account | ✅ done |
| GitHub PAT | repo, project, issues scopes | ✅ done |
| Ollama | Already installed | ✅ done |
| opencode | Already configured | ✅ done |

## 7. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-28 | `opencode/deepseek-v4-flash-free` as default | Reliable for session titles |
| 2026-06-28 | Qwen 2.5 Coder 7B as primary local model | No reasoning issue, best code |
| 2026-06-28 | streaming:false for Qwen 3.5 | Fixes reasoning leak |
| 2026-06-28 | GitHub Projects for project mgmt | Free, native MCP support |
| 2026-07-05 | Web-only (remove WhatsApp bridge) | Simpler, local-only, no external dependency |
| 2026-07-05 | Flask as web server | Stdlib-compatible, minimal setup |

## 8. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| 16 GB RAM insufficient for dual model | Medium | Medium | One model at a time |
| MacBook sleep | Medium | Medium | Keep browser active or caffeinate |
| GitHub MCP token expires | Low | High | Document renewal, gh CLI fallback |
| MCP context window consumption | High | Medium | Enable only needed MCPs per agent |
