# SYS2 - Technical Design & Implementation Plan

## 1. Implementation Phases

| Phase | Name | Duration (est.) | Dependencies |
|-------|------|-----------------|--------------|
| SWE1 | Local Model Setup & opencode Integration | 1-2 days | None |
| SWE2 | WhatsApp Bot & End-to-End Automation | 3-5 days | SWE1 |

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

| Server | Purpose |
|--------|---------|
| `@anthropic/mcp-filesystem` | File read/write/search |
| Local shell MCP | Command execution |
| Custom WhatsApp MCP | Message send/receive (SWE2) |
| macOS automation MCP | AppleScript, shortcuts |

## 4. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-28 | Use `opencode/deepseek-v4-flash-free` as default | Works reliably for session titles & small tasks |
| 2026-06-28 | Qwen 2.5 Coder 7B as primary local model | No reasoning issue, best code quality |
| 2026-06-28 | Defer Qwen 3.5 reasoning fix to SWE1 | Need to test `streaming: false` at provider level |
| 2026-06-28 | No proxy/bash scripts | User preference for clean config-only setup |

## 5. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `streaming: false` doesn't fix Qwen 3.5 | Medium | High | Use Modelfile approach (no download) |
| 16 GB RAM insufficient for dual model use | Medium | Medium | Load one model at a time |
| WhatsApp API changes/bans | Low | High | Use WhatsApp Web JS as fallback |
| MacBook goes to sleep | Medium | Medium | Use `caffeinate` or power management |
