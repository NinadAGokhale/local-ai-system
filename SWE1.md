# SWE1 — Phase 1: Local Model Setup & opencode Integration

## Status: ✅ Complete

**Objective:** Get all 3 local Ollama models working with opencode, accessible via web UI model dropdown.

## Result
- All models work via `streaming: false` provider config (fixes Qwen 3.5 reasoning leak)
- Web UI model dropdown lists all Ollama models + opencode cloud models
- 362 skills loaded, 35 agents available
- 72 unit tests passing

## Model Setup

| Model | Status | Notes |
|-------|--------|-------|
| `qwen2.5-coder:7b` | ✅ Works | Default, best code quality |
| `qwen3.5:4b` | ✅ Works | streaming:false in config |
| `qwen3.5:9b` | ✅ Works | streaming:false in config |
| `opencode/deepseek-v4-flash-free` | ✅ Works | Cloud model via opencode CLI |

## Task List

### Task 1.1: Verify provider-level `streaming: false`

**Current config:** `~/.config/opencode/opencode.jsonc` has `"streaming": false` at provider level.

**Test:**
1. Launch opencode TUI
2. `/model ollama/qwen3.5:4b`
3. Ask "hello"
4. Check if response text appears (not just "Thought: 4ms / The")

**Expected:** Non-streaming API call returns full JSON with both `content` and `reasoning`. `simulateStreamingMiddleware` should extract `content` only.

**If it fails:** Proceed to Task 1.2

### Task 1.2: Create local non-thinking Modelfile (no download)

This approach uses the **existing model blob** on disk — no download needed.

**Step-by-step:**

```bash
# 1. Get the blob path for qwen3.5:4b
ollama show qwen3.5:4b
# Look for: FROM /Users/ninadgokhale/.ollama/models/blobs/sha256-xxxxx

# 2. Create a Modelfile that references the blob WITHOUT RENDERER/PARSER
cat > ~/Desktop/local-ai-system/Modelfile.qwen3.5-4b-instruct << 'EOF'
FROM /Users/ninadgokhale/.ollama/models/blobs/sha256-2a654d98e6fb
TEMPLATE {{ .Prompt }}
PARAMETER top_p 0.95
PARAMETER presence_penalty 1.5
PARAMETER temperature 1
PARAMETER top_k 20
EOF

# 3. Create the new model
ollama create qwen3.5:4b-instruct -f ~/Desktop/local-ai-system/Modelfile.qwen3.5-4b-instruct

# 4. Test streaming
curl http://localhost:11434/v1/chat/completions \
  -d '{"model":"qwen3.5:4b-instruct","messages":[{"role":"user","content":"hi"}],"stream":true}'

# 5. Add to opencode config
```

**Why this works:** The official `qwen3.5:4b` uses `RENDERER qwen3.5` / `PARSER qwen3.5` which enables thinking. By omitting these directives and pointing directly to the blob, Ollama falls back to a default template renderer that doesn't trigger thinking mode.

**Repeat for qwen3.5:9b:**
```bash
ollama show qwen3.5:9b
# Get blob path and repeat steps 2-5
```

### Task 1.3: Update opencode config with all models

Edit `~/.config/opencode/opencode.jsonc`:

```jsonc
{
  "provider": {
    "ollama": {
      "options": {
        "baseURL": "http://localhost:11434/v1",
        "streaming": false
      },
      "models": {
        "qwen3.5:4b-instruct": { "name": "Qwen 3.5 4B (Non-thinking)" },
        "qwen3.5:9b-instruct": { "name": "Qwen 3.5 9B (Non-thinking)" },
        "qwen2.5-coder:7b":    { "name": "Qwen 2.5 Coder 7B" },
        "qwen3.5:4b":          { "name": "Qwen 3.5 4B (Thinking)" },
        "qwen3.5:9b":          { "name": "Qwen 3.5 9B (Thinking)" }
      }
    }
  }
}
```

### Task 1.4: Create opencode Skills

Create skill files in `~/.config/opencode/skills/`:

**system-admin.md** — File system operations, process management, brew management
**macos-control.md** — AppleScript automation, notifications, window management
**development.md** — Git operations, coding tasks, project scaffolding
**general-assistant.md** — General Q&A, task decomposition, planning

Each skill follows the opencode skill markdown format with `---` frontmatter:

```markdown
---
name: system-admin
description: System administration tasks for macOS
---
You are a macOS system administrator assistant. You have access to:
- Shell commands (zsh/bash)
- File system operations
- Homebrew package management
...
```

### Task 1.5: Test all models

| Model | Task | Expected | Status |
|-------|------|----------|--------|
| `qwen2.5-coder:7b` | "Write a Python script" | Code output | ✅ Already works |
| `qwen3.5:4b-instruct` | "Explain quantum computing" | Text response | ⏳ Test after Modelfile |
| `qwen3.5:9b-instruct` | "Debug this code: ..." | Debug output | ⏳ Test after Modelfile |

### Task 1.6: Model Selection Strategy

Configure which model is used for which agent role:

| Role | Model | Reason |
|------|-------|--------|
| Title generation | `opencode/deepseek-v4-flash-free` | Fast, small, always available |
| Build agent (coding) | `ollama/qwen2.5-coder:7b` | Best code quality, no reasoning issue |
| General agent (Q&A) | `ollama/qwen3.5:4b-instruct` | Good general knowledge, fast |
| Complex reasoning | `ollama/qwen3.5:9b-instruct` | Best reasoning, but slower |

## Verification Checklist

- [ ] `opencode` launches without errors
- [ ] `/model ollama/qwen2.5-coder:7b` shows responses correctly
- [ ] `/model ollama/qwen3.5:4b-instruct` shows responses (no reasoning leak)
- [ ] `/model ollama/qwen3.5:9b-instruct` shows responses (no reasoning leak)
- [ ] Skills are loaded and accessible via `/skill` command
- [ ] Switching models via `/model` works mid-session
- [ ] Tool calls (shell, file ops) work with local models
