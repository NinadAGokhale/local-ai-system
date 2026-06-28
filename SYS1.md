# SYS1 - System Requirements & Architecture

## 1. System Overview

**Project:** Local AI System — End-to-end automation via WhatsApp bot
**Goal:** Run a fully local AI system on MacBook that can be controlled via WhatsApp messages, executing actions across the OS using opencode with custom skills, MCP tools, and agents.
**Date:** 2026-06-28
**Status:** Design Phase

## 2. Hardware & OS Specifications

| Component | Detail |
|-----------|--------|
| **Model** | MacBookPro18,3 (14-inch, 2021) |
| **SoC** | Apple M1 Pro — 10 cores (8 performance + 2 efficiency) |
| **RAM** | 16 GB unified memory |
| **Storage** | ~926 GB SSD (461 GB free) |
| **OS** | macOS 26.0.1 (Build 25A362) |
| **Shell** | Zsh |

## 3. Installed Software Inventory

### Core Tools
| Tool | Version | Purpose |
|------|---------|---------|
| Homebrew | 6.0.5 | Package manager |
| Node.js | v25.9.0 | JavaScript runtime |
| Python 3 | 3.11.5 | Python runtime |
| Git | 2.50.1 | Version control |
| npm | 11.12.1 | Node package manager |

### AI/LLM Stack
| Tool | Version | Purpose |
|------|---------|---------|
| Ollama | 0.30.10 | Local LLM server |
| opencode | 1.17.11 | AI coding agent (TUI) |
| codex | 0.42.0 | AI CLI tool |
| openclaw | 2026.4.9 | AI agent platform |

### Local Ollama Models
| Model | Size | Type |
|-------|------|------|
| `qwen3.5:4b` | 3.4 GB | Reasoning (hybrid) |
| `qwen3.5:9b` (same as `qwen3.5:latest`) | 6.6 GB | Reasoning (hybrid) |
| `qwen3.5:4b-chat` | 3.4 GB | Reasoning (hybrid) |
| `qwen2.5-coder:7b` | 4.7 GB | Non-reasoning (instruction) |

### Applications (Non-Apple)
ChatGPT, Cursor, Dropover, Google Chrome, Microsoft Office suite, OneDrive, Ollama, Perplexity, Surfshark VPN, Visual Studio Code, VLC, WhatsApp, Zoom

### Auto-Start Login Items
QuickTime Player, Visual Studio Code, Comet, Dropover

## 4. Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User (WhatsApp)                    │
└──────────────────────┬──────────────────────────────┘
                       │ Message
                       ▼
┌─────────────────────────────────────────────────────┐
│              WhatsApp Bot (Python/Node)               │
│   - Receives messages via WhatsApp Web API             │
│   - Parses commands/intent                            │
│   - Forwards to opencode CLI                          │
└──────────────────────┬──────────────────────────────┘
                       │ Command
                       ▼
┌─────────────────────────────────────────────────────┐
│                  opencode CLI                         │
│  ┌─────────────────────────────────────────────────┐│
│  │  Agents (Build, General, Custom)                 ││
│  │  Skills (.md instruction files)                  ││
│  │  MCP Servers (filesystem, shell, etc.)           ││
│  └──────────┬──────────────────────────────────────┘│
└──────────────┼──────────────────────────────────────┘
               │ API Call
               ▼
┌─────────────────────────────────────────────────────┐
│              Ollama Server (localhost:11434)          │
│  ┌─────────────────────────────────────────────────┐│
│  │  qwen2.5-coder:7b  (coding tasks)                ││
│  │  qwen3.5:4b        (lightweight reasoning)       ││
│  │  qwen3.5:9b        (heavy reasoning)             ││
│  └─────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

## 5. Data Flow

1. **User** sends WhatsApp message to bot number
2. **WhatsApp Bot** receives message via WhatsApp Web/API
3. **Command Parser** extracts intent and parameters
4. **Router** determines which opencode agent/skill to invoke
5. **opencode** executes the command using selected local model (via Ollama)
6. **Skills/MCP** provide additional context and tool access
7. **Result** is captured and sent back to user via WhatsApp

## 6. Security Boundaries

- All LLM inference runs **locally** (no cloud API calls)
- Ollama listens on `localhost:11434` only
- WhatsApp bot communicates with opencode CLI via local IPC/filesystem
- No credentials leave the machine
- MCP server permissions can be scoped per skill

## 7. Constraints & Known Issues

| Issue | Impact | Status |
|-------|--------|--------|
| Qwen 3.5 models emit reasoning before content | opencode SDK reads reasoning as text | **Unresolved** — see SWE1 |
| Qwen 2.5 Coder 7B works perfectly | No reasoning output | ✅ Works |
| 16 GB RAM limits concurrent model loading | Only one ~7B model at a time | Acceptable |
| WhatsApp bot needs always-on connection | MacBook must stay awake/connected | Consider sleep prevention |

## 8. Design Principles

1. **Local-first** — All processing happens on-device
2. **No cloud dependencies** — OpenAI/Anthropic not required for core flow
3. **Modular** — Each component is independently replaceable
4. **Minimal downloads** — Use existing model blobs where possible
5. **Fail-fast** — If a model doesn't work, fall back to working one
