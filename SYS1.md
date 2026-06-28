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

## 8. Agent Architecture

### 8.1 Agent Roles

The system uses specialized agents, each backed by a specific local model and MCP toolset:

```
User Input (WhatsApp / TUI)
        │
        ▼
┌─────────────────────────────────────────────┐
│  Persona 1: Architect Agent                  │
│  Model: qwen3.5:9b (strong reasoning)        │
│  Role: Takes user's high-level intent,       │
│        creates SYS/SWE requirement docs,     │
│        breaks into GitHub Issues, creates    │
│        GitHub Project board items            │
│  MCP: GitHub (issues, projects write)        │
└──────────────┬──────────────────────────────┘
               │ Creates GitHub Project items
               ▼
┌─────────────────────────────────────────────┐
│  GitHub Project Board                         │
│  Columns: Backlog → To Do → In Progress →    │
│           Review → Done                      │
│  Items: GitHub Issues with labels            │
└──────────────┬──────────────────────────────┘
               │ Agents pick up tasks
               ▼
┌─────────────────────────────────────────────┐
│  Persona 2: Coding Agent                     │
│  Model: qwen2.5-coder:7b (code)              │
│  MCP: GitHub, Filesystem, Shell              │
│  Role: Implements code tasks from issues     │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  Persona 3: System Agent                     │
│  Model: qwen3.5:4b (general)                 │
│  MCP: Shell, macOS AppleScript, Filesystem   │
│  Role: macOS operations, file mgmt, config   │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  Persona 4: DevOps Agent                     │
│  Model: qwen3.5:4b                           │
│  MCP: GitHub (Actions, Releases), Shell      │
│  Role: CI/CD, deployment, git operations     │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  Persona 5: WhatsApp Bridge Agent            │
│  Model: qwen3.5:4b                           │
│  MCP: WhatsApp (custom), opencode CLI        │
│  Role: Translates WhatsApp msgs to tasks     │
└─────────────────────────────────────────────┘
```

### 8.2 Agent-Model Mapping

| Persona | Model | MCP Servers | Trigger |
|---------|-------|-------------|---------|
| Architect | `qwen3.5:9b` | GitHub (projects+issues) | User high-level input |
| Coding | `qwen2.5-coder:7b` | GitHub, Filesystem, Shell | GitHub issue assigned |
| System | `qwen3.5:4b` | Shell, AppleScript, Filesystem | GitHub issue assigned |
| DevOps | `qwen3.5:4b` | GitHub (Actions), Shell | GitHub issue / PR event |
| WhatsApp Bridge | `qwen3.5:4b` | WhatsApp, opencode CLI | Incoming WhatsApp message |

## 9. Project Management Integration

### 9.1 Tool Choice: GitHub Projects (Free)

| Feature | Detail |
|---------|--------|
| **Tool** | GitHub Projects (Projects v2) |
| **Cost** | Free with any GitHub account |
| **GitHub Sync** | Native — Issues, PRs, and repos are first-class |
| **MCP Support** | ✅ GitHub MCP Server (official, supports `projects` toolset) |
| **MCP Tools** | List/get projects, create/update items, manage fields, move between columns |
| **Alternative** | `Arclio/github-projects-mcp` — dedicated Projects MCP server |

### 9.2 Project Board Schema

```
GitHub Project: "Local AI System"
├── Field: Status (To Do / In Progress / Review / Done)
├── Field: Phase (SWE1 / SWE2 / SWE3)
├── Field: Persona (Architect / Coding / System / DevOps / Bridge)
├── Field: Priority (P0 / P1 / P2)
│
├── Item: [Task] Set up non-thinking Qwen 3.5 Modelfile
│   ├── Type: Issue
│   ├── Status: To Do
│   ├── Phase: SWE1
│   └── Persona: System
│
└── Item: [Epic] WhatsApp Bot Integration
    ├── Type: Draft Issue
    ├── Status: Backlog
    ├── Phase: SWE2
    └── Persona: Bridge
```

### 9.3 Agent Workflow

1. **User** provides high-level input (WhatsApp or TUI)
2. **Architect Agent** (Persona 1) analyzes input, creates SYS/SWE .md files AND GitHub Issues with proper labels/phases
3. **GitHub Project** automatically picks up new issues into "Backlog"
4. **Task Agents** (Coding/System/DevOps) poll or are triggered by new issues
5. **Agent selects task** from "To Do" column, moves it to "In Progress"
6. **Agent executes task** using its model + MCP tools
7. **Agent marks task** "Review" or "Done" with a comment/PR
8. **Architect Agent** periodically reviews board for consistency

## 10. Design Principles

1. **Local-first** — All processing happens on-device
2. **No cloud dependencies** — OpenAI/Anthropic not required for core flow
3. **Modular** — Each component is independently replaceable
4. **Minimal downloads** — Use existing model blobs where possible
5. **Fail-fast** — If a model doesn't work, fall back to working one
6. **Project-driven** — All work is tracked in GitHub Projects, agents pull tasks from the board
7. **MCP-native** — All integrations use MCP servers for tool access
