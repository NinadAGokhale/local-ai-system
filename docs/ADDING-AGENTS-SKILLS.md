# Adding Agents & Skills

## The Bifurcation (tl;dr)

| | Agent | Skill |
|---|---|---|
| **What** | A persona with tool access | A knowledge/instruction bundle |
| **Storage** | `~/.config/opencode/agents/{name}.md` | `~/.config/opencode/skills/{name}/SKILL.md` |
| **Can execute** | Yes — calls tools, runs sub-agents | No — pure reference |
| **Can stack** | No — one at a time | Yes — multiple at once |

## Adding an Agent

### 1. Create the file

```
~/.config/opencode/agents/my-agent.md
```

### 2. Required frontmatter

```yaml
---
name: my-agent
description: "What this agent does, when to use it"
tools:
  Read: true
  Write: true
  Bash: true
  Grep: true
  Glob: true
---
```

Only the tools your agent actually needs. If it doesn't write files, omit `Write`.

### 3. Persona content (after frontmatter)

Write the persona in plain text. Be specific about:
- **Role & Expertise** — what domain, what level
- **Behavioral rules** — how it should respond (concise, structured, etc.)
- **Tools guidance** — when to use each tool

Example:

```markdown
# My Agent

## Role & Expertise
You are a senior [domain] specialist. You handle [specific tasks].

## Behavioral Rules
- Always verify assumptions before coding
- Be concise, never verbose
- Never generate URLs

## Tools
- Read: inspect existing files before making changes
- Write: only when explicitly asked
```

### 4. Add an alias (optional)

Edit `src/core/command_parser.py` and add to `AGENT_ALIASES`:

```python
AGENT_ALIASES = {
    ...
    "my": "my-agent",
    "alias": "my-agent",
}
```

The alias is what users type after `@` or `agent:` — short names like `@my` or `@engineer`.

### 5. Auto-discovery

The UI fetches `/api/agents` which lists all `.md` files in `~/.config/opencode/agents/`. Your new agent appears automatically — no restart needed, just refresh the page.

---

## Adding a Skill

### 1. Create the directory and file

```
~/.config/opencode/skills/my-skill/SKILL.md
```

The directory name becomes the skill name that users type as `$my-skill`.

### 2. Optional frontmatter

```yaml
---
name: my-skill
description: "What this skill does — appears in the autocomplete dropdown"
---
```

### 3. Methodology content (after frontmatter)

Write pure instructions — no persona, no tool definitions. Focus on:

- **When to invoke** — trigger phrases, use cases
- **Procedure** — step-by-step methodology
- **Rules / constraints** — things to avoid, things to always do
- **Examples** — what good output looks like

Example:

```markdown
# My Skill

**Optimize X for Y.** Use when the user asks about [topic].

## Triggers
- "audit my X"
- "optimize Y for Z"

## Process
1. Analyze the current state
2. Identify gaps against best practices
3. Prioritize fixes by impact
4. Generate report

## Rules
- Always cite specific sources
- Never invent metrics — only use what's observable
```

### 4. Auto-discovery

The UI fetches `/api/skills` which lists all directories under `~/.config/opencode/skills/` that contain a `SKILL.md`. Your new skill appears automatically.

---

## Frequently Asked Questions

### Can a skill have "You are an expert" in it?

Yes — some existing skills use this language. It's harmless (the content is treated as reference instructions), but for purity the methodology content should avoid persona framing.

### How do I stack multiple skills?

Select multiple `$skill` from the autocomplete or catalogue. Each adds a badge. The prompt includes all selected skills as reference material under the active agent.

### Can an agent use a skill internally?

Yes — agents reference their own skills in their `.md` content (e.g., `cs-engineering-lead.md` lists skills it integrates). These are documentation notes, not enforced at the code level. The user selects which skills to activate.

### What if a skill has sub-pages or scripts?

The directory can contain anything (`scripts/`, `templates/`, etc.). Only `SKILL.md` is loaded as instruction content. Supporting files are ignored by the loader but available if needed.

### How do I test a new agent or skill?

Use the debug endpoint:

```bash
curl http://127.0.0.1:5002/api/debug/resolve \
  -X POST -H 'Content-Type: application/json' \
  -d '{"message":"agent: my-agent: test task","model":"ollama/qwen3.5:4b"}'
```

This shows what content will be loaded, how it will be routed, and the final call target without executing the LLM.
