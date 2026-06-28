# SYS2 - Technical Design & Implementation Plan

## 1. Implementation Phases

| Phase | Name | Duration (est.) | Dependencies |
|-------|------|-----------------|--------------|
| SWE0 | GitHub + opencode MCP Setup | 1 hour | GitHub account |
| SWE1 | Local Model Setup & opencode Integration | 1-2 days | SWE0 |
| SWE2 | WhatsApp Bot & End-to-End Automation | 3-5 days | SWE1 |
| SWE3 | Agent Architecture & GitHub Project Automation | 2-3 days | SWE0, SWE1 |

## 2. Model Analysis & Strategy

### 2.1 Model Comparison

| Criteria | qwen3.5:4b | qwen3.5:9b | qwen2.5-coder:7b |
|----------|------------|------------|-------------------|
| **Size** | 3.4 GB | 6.6 GB | 4.7 GB |
| **RAM usage** | ~4 GB | ~8 GB | ~6 GB |
| **Reasoning output** | Yes (hybrid) | Yes (hybrid) | No (instruct only) |
| **Works with opencode today** | ❌ (reasoning issue) | ❌ (reasoning issue) | ✅ |
| **Speed** | Fast (~10 tok/s) | Medium (~6 tok/s) | Fast (~12 tok/s) |
| **Code quality** | Good | Very Good | Excellent |
| **General reasoning** | Excellent | Excellent | Moderate |

### 2.2 Reasoning Model Problem

**Root Cause:** Qwen 3.5 models are hybrid-thinking models. During streaming, they emit `reasoning` tokens in a separate field before `content`. opencode's AI SDK reads the first `reasoning` token as the response text and exits prematurely.

**Approaches Considered:**
| Approach | Status | Reason |
|----------|--------|--------|
| Config: `interleaved: { field: "reasoning" }` | ❌ Failed | Doesn't change SDK's chunk-parsing behavior |
| Config: `streaming: false` (provider level) | ⚠️ Untested | May work via `simulateStreamingMiddleware` |
| Proxy: non-streaming → SSE | ❌ Rejected | User wants no bash/proxy |
| Model: `sorc/qwen3.5-instruct` | ⏳ Pending | Need download (slow connection) |
| Model: Local Modelfile (no RENDERER/PARSER) | 🔜 Plan B | Uses existing blob, no download needed |

### 2.3 Recommendation

**Default model:** `qwen2.5-coder:7b` — works out of the box, excellent code quality
**Secondary model:** Qwen 3.5 (4b or 9b) — once reasoning issue is resolved
**Strategy:** Fix reasoning issue via provider-level `streaming: false` or local Modelfile approach

## 3. Component Architecture

### 3.1 opencode Configuration

```jsonc
// ~/.config/opencode/opencode.jsonc
{
  "model": "opencode/deepseek-v4-flash-free",     // Default (cloud)
  "small_model": "opencode/deepseek-v4-flash-free",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1",
        "headerTimeout": 180000,
        "chunkTimeout": 180000,
        "streaming": false          // For Qwen 3.5 compatibility
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

### 3.2 Skills Structure

```
~/.config/opencode/skills/
├── system-admin.md       # File system, process management
├── macos-control.md      # macOS-specific actions (AppleScript, automation)
├── development.md        # Git, coding, project management
├── whatsapp-bridge.md    # WhatsApp message handling (for SWE2)
└── general-assistant.md  # General Q&A, task planning
```

### 3.3 MCP Servers (planned)

| Server | Type | Purpose | Phase |
|--------|------|---------|-------|
| **GitHub MCP** (remote) | Remote | GitHub Issues, Projects, Repos, PRs | SWE0 |
| `@anthropic/mcp-filesystem` | Local | File read/write/search | SWE1 |
| Local shell MCP | Local | Command execution | SWE1 |
| macOS automation MCP | Local | AppleScript, shortcuts | SWE1 |
| Custom WhatsApp MCP | Local | Message send/receive | SWE2 |

### 3.4 GitHub MCP Configuration (opencode.jsonc)

```jsonc
{
  "mcp": {
    "github": {
      "type": "remote",
      "command": ["node", "path/to/github-mcp-server"],
      "enabled": true,
      "environment": {
        "GITHUB_TOKEN": "{env:GITHUB_TOKEN}"
      }
    }
  }
}
```

Credentials needed from user:
- GitHub account (create one at github.com if none)
- GitHub Personal Access Token (classic) with scopes: `repo`, `project`, `issues`, `read:org`
  - Create at: https://github.com/settings/tokens
  - Store in shell profile: `export GITHUB_TOKEN="ghp_..."`
  - Or use `gh auth login` for CLI-based auth

## 4. GitHub Project Board Schema

### 4.1 Board Structure

```
Project: "Local AI System" (GitHub Projects v2)
├── Status: Backlog → To Do → In Progress → Review → Done
├── Phase: SWE0 / SWE1 / SWE2 / SWE3 (Single Select)
├── Persona: Architect / Coding / System / DevOps / Bridge (Single Select)
├── Priority: P0 / P1 / P2 (Single Select)
└── Agent: (text field — assigned agent name)
```

### 4.2 Task Lifecycle

```
User Input → Architect Agent
  → Creates GitHub Issue with labels (phase, persona, priority)
  → Issue auto-appears in "Backlog"
  → Manual/auto-move to "To Do"
  → Task Agent picks up → moves to "In Progress"
  → Agent creates branch/PR → moves to "Review"
  → PR merged → moves to "Done"
```

### 4.3 MCP Tools for Project Management

| Tool Source | Tools Available |
|-------------|-----------------|
| GitHub MCP Server (remote) | `issues_read`, `issues_write`, `pull_request_read`, `pull_request_write` |
| GitHub MCP `projects` toolset | List projects, get items, update item fields, add/remove items |
| `Arclio/github-projects-mcp` (optional) | Project item CRUD, field management, board operations |

## 5. Credentials & Accounts Checklist

| Service | What's Needed | How to Get | Status |
|---------|---------------|------------|--------|
| **GitHub** | Free account | https://github.com/signup | ⏳ User action |
| **GitHub PAT** | Token with `repo`, `project`, `issues` scopes | https://github.com/settings/tokens | ⏳ User action |
| **Ollama** | Already installed | — | ✅ Done |
| **opencode** | Already configured | — | ✅ Done |
| **npm** | Already installed | — | ✅ Done |
| **WhatsApp** | Phone number (already have) | — | ✅ Done |

## 6. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-28 | Use `opencode/deepseek-v4-flash-free` as default | Works reliably for session titles & small tasks |
| 2026-06-28 | Qwen 2.5 Coder 7B as primary local model | No reasoning issue, best code quality |
| 2026-06-28 | Defer Qwen 3.5 reasoning fix to SWE1 | Need to test `streaming: false` at provider level |
| 2026-06-28 | No proxy/bash scripts | User preference for clean config-only setup |
| 2026-06-28 | **GitHub Projects** as project management tool | Free, native GitHub integration, official MCP server |
| 2026-06-28 | **GitHub MCP Server (remote)** for agent-project bridge | Official, supports projects toolset, no Docker needed |
| 2026-06-28 | **Architect Agent (Persona 1)** creates SYS/SWE from user input | Automates requirements decomposition |
| 2026-06-28 | **5 Persona model** for agent specialization | Match model strength to task type |
| 2026-06-28 | Tasks flow: GitHub Issue → Project Board → Agent picks up → Executes → Marks done | Clear traceability, async execution |

## 7. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `streaming: false` doesn't fix Qwen 3.5 | Medium | High | Use Modelfile approach (no download) |
| 16 GB RAM insufficient for dual model use | Medium | Medium | Load one model at a time |
| WhatsApp API changes/bans | Low | High | Use WhatsApp Web JS as fallback |
| MacBook goes to sleep | Medium | Medium | Use `caffeinate` or power management |
| GitHub MCP token expires/revoked | Low | High | Document renewal process, use `gh` CLI fallback |
| GitHub Projects API rate limits | Low | Medium | Batch updates, cache project state |
| MCP context window consumption | High | Medium | Enable only needed MCP servers per agent persona |
