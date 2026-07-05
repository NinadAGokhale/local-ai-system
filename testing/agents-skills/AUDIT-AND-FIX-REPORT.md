# Agents & Skills — Audit, Fix & Test Report

## Root Cause

**Skills were never loaded.** The `$skill` prefix was just syntactic sugar — it prepended `[skill: X]` as text to the prompt. The actual `SKILL.md` file (hundreds of lines of instructions) was never read from disk.

**Agents were fake for Ollama models.** `@agent` with an Ollama model just said `"You are acting as the agent 'X'."` as a plain text prefix. The agent's `.md` file (personality, tools, system prompt) was never loaded. Only `opencode run --agent` (cloud models) did real agent loading.

## What Was Changed

### 1. New file: `src/core/content_loader.py`
Two helpers that read agent `.md` and skill `SKILL.md` files from disk:
- `get_skill_content(name)` — reads `~/.config/opencode/skills/<name>/SKILL.md`, strips YAML frontmatter
- `get_agent_content(name)` — reads `~/.config/opencode/agents/<name>.md`, strips YAML frontmatter

### 2. Changed: `src/core/handler.py`
- **Skill path** (line 55–65): Instead of `run_opencode(f"[skill: {name}] {task}")`, now reads `SKILL.md` content and prepends `[Skill: {name}]\n{content[:4000]}\n\nTask: {task}` as context
- **Combined skill+agent path**: Skill content loaded the same way, task wrapped with `execute_agent` instead
- **Agent Ollama path** (line 145): Instead of `f"You are acting as '{name}'. {task}"`, now reads agent `.md` content and includes `{content[:4000]}` as the agent's personality/instructions

### 3. Changed: `src/web/dashboard.py`
- Added `/api/debug/resolve` endpoint for diagnosing message routing without executing LLM
- Shows: `cmd_type`, `resolved_model`, `skill_name`, `agent_name`, `skill_content_chars`, `agent_content_chars`, `_will_call`

## Test Results

### Resolution test (all 11 agents — content loaded?)
```
  cto          -> startup-cto               ( 8764 chars) [OK]
  growth       -> growth-marketer           ( 9211 chars) [OK]
  founder      -> solo-founder              ( 9579 chars) [OK]
  engineer     -> cs-engineering-lead       ( 3037 chars) [OK]
  frontend     -> cs-frontend-engineer      ( 7223 chars) [OK]
  backend      -> cs-backend-engineer       ( 8076 chars) [OK]
  fullstack    -> cs-fullstack-engineer     ( 9972 chars) [OK]
  product      -> cs-product-manager        (30722 chars) [OK]
  project      -> cs-project-manager        (25182 chars) [OK]
  qa           -> cs-quality-regulatory     ( 3474 chars) [OK]
  devops       -> devops-engineer           ( 4728 chars) [OK]
```
**All 11 agents load actual file content.** ✓

### Resolution test (sample skills — content loaded?)
```
  aeo                    (10190 chars) [OK]
  seo-audit              ( 7042 chars) [OK]
  content-production     (10677 chars) [OK]
  landing                (13886 chars) [OK]
  copywriting            ( 9704 chars) [OK]
  email-sequence         ( 5362 chars) [OK]
```
**All 6 skills load actual SKILL.md content.** ✓

### Routing test (models × modes)
| Scenario | cmd_type | Skill Loaded | Agent Loaded | Routes To |
|----------|----------|-------------|-------------|-----------|
| Plain | explain | N/A | N/A | run_opencode → ollama |
| Agent + Ollama | agent | — | ✓ 8764c | run_ollama (agent) |
| Agent + Cloud | agent | — | ✓ 3037c | run_agent (~CLI) |
| Skill + Ollama | skill | ✓ 10190c | — | run_ollama (skill) |
| Skill + Cloud | skill | ✓ 10190c | — | run_opencode (skill) |
| Combined + Cloud | skill | ✓ 10190c | ✓ 3037c | execute_agent (CLI) |
| Combined + Ollama | skill | ✓ 10190c | ✓ 3037c | execute_agent (agent) |

### Live inference comparison (Ollama)
| Context | Response | Verdict |
|---------|----------|---------|
| Plain (no context) | "I am a helpful assistant providing direct text responses only via this WhatsApp chat." | Generic |
| Agent `startup-cto` | "I am a technical Co-founder focused on shipping software fast." | **Uses agent identity** |
| Skill `aeo` | "AEO optimizes content so LLMs cite it authoritatively; unlike SEO that ranks pages for human clicks." | **Uses skill knowledge** |

## Known Issue: opencode cloud `--agent` API Error

The opencode CLI `--agent` flag returns:
```json
{"name": "UnknownError", "data": {"message": "Unexpected server error..."}}
```
This is an upstream API error (rate limit or server-side issue), not our code. Our `run_agent()` correctly falls back to `run_opencode_cli()` with `--model` in this case, so the user still gets a response — just without full agent context.

**Workaround**: Use Ollama models for agent/skill mode (where our fix now loads the actual file content), or use opencode cloud without agent (`$skill` mode which also works).

## Files Changed
| File | Change |
|------|--------|
| `src/core/content_loader.py` | **NEW** — reads agent .md and skill SKILL.md from disk |
| `src/core/handler.py` | Inject actual file content instead of text prefixes |
| `src/web/dashboard.py` | Added `/api/debug/resolve` endpoint, imported AGENT_ALIASES |
