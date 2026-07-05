# Agents & Skills — Testing & Audit Plan

## Goal
Verify whether agents and skills are actually being loaded/used at the backend, not just displayed in the UI. Fix any gaps found.

## Current Architecture (suspects)

### Skill flow (`$skill`)
1. Frontend sets `currentSkill = "some-skill"` via POST `/api/skill`
2. Backend stores it in session
3. On chat send, backend prepends `skill: some-skill: {message}`
4. `parse_command` matches `skill:` → `SKILL` type
5. `_handle_message` for `SKILL`: extracts skill name, calls `run_opencode("[skill: some-skill] {message}")`
6. **Result**: skill is just a text prefix `[skill: X]`. The actual `SKILL.md` file is **NEVER read or injected**.

### Agent flow (`@agent`)
1. Frontend sets `currentAgent = "engineer"` via POST `/api/agent`
2. On chat send, backend prepends `agent: engineer: {message}`
3. `parse_command` matches `agent:` → `AGENT` type
4. `execute_agent("engineer: {message}", model)`:
   - **opencode cloud model**: runs `opencode run --agent cs-engineering-lead --auto "{message}"` → **works correctly**
   - **Ollama model**: runs `run_ollama("You are acting as the agent 'cs-engineering-lead'. {message}")` → **fake — agent file never loaded**

### Combined flow (`$skill` + `@agent`)
- Backend prepends both but routes through `execute_agent` with skill name in brackets as text → **skill never actually loaded**

## Test Matrix

### Models
| ID | Type | Backend |
|----|------|---------|
| `opencode/deepseek-v4-flash-free` | Cloud | opencode CLI |
| `ollama/qwen2.5-coder:7b` | Local | direct Ollama API |
| `ollama/qwen3.5:4b` | Local | direct Ollama API |

### Modes
| Mode | Test Case |
|------|-----------|
| No agent/skill | Plain message → run_opencode |
| `@engineer` only | Agent → execute_agent → opencode CLI or Ollama |
| `$aeo` skill only | Skill → run_opencode with `[skill: aeo]` prefix |
| `@engineer` + `$aeo` | Combined → execute_agent with skill in prompt |

### Success Criteria
For each combination, verify:
- [ ] Correct backend route is called (`run_opencode` vs `execute_agent` vs `run_ollama`)
- [ ] Agent `.md` file content is included in context (for Ollama mode)
- [ ] Skill `SKILL.md` content is included in context
- [ ] Response is NOT generic — reflects the agent persona / skill instructions

## Deliverables
1. Audit report of current backend routing (`testing/agents-skills/AUDIT.md`)
2. Fixed skill loading — read `SKILL.md` and inject into context
3. Fixed Ollama agent loading — read agent `.md` and inject into context
4. Test API endpoint for manual verification
