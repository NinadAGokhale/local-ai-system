# Agent vs Skill — Logical Bifurcation

## The Core Distinction

| | **Agent** | **Skill** |
|---|---|---|
| **What it is** | A configured persona | A knowledge/instruction bundle |
| **Analogous to** | A subject-matter expert with tools | A reference manual / methodology guide |
| **Has identity** | Yes — "You are a senior engineer..." | No — just instructions |
| **Has tool access** | Yes — Read, Write, Bash, Grep, Glob | No — tools come from the running agent |
| **Has domain scope** | Yes — engineering, marketing, product, etc. | Yes — but narrow (one technique) |
| **Behavioral rules** | Yes — "Be concise", "Never guess URLs" | No — just methodology rules |
| **Can be stacked** | No — only ONE agent at a time (single persona) | Yes — MULTIPLE skills can be combined |
| **Granularity** | Broad role (covers full domain) | Narrow capability (one task/methodology) |
| **Execution** | Orchestrates work, calls tools, forks subagents | Provides instructions for the agent to follow |
| **Example** | `@engineer` (cs-engineering-lead) | `$aeo` (how to optimize for AI citation) |

## How They Interact

```
Agent = WHO does the work
Skill  = WHAT knowledge/methodology to use
────────────────────────────────────
Agent (persona) ─── executes task ─── using Skill (instructions) as reference
```

The agent is the **executor**. Skills are **knowledge sources** that the agent consults to perform the task correctly.

You pick ONE agent (your executor persona) and optionally add ONE OR MORE skills (reference instructions).

## Why It Matters

### Before the fix
- `"skill: aeo: audit our homepage"` → just prepended `[skill: aeo]` as text
- `"agent: engineer: audit our homepage"` → ran `opencode --agent cs-engineering-lead --auto "task"`
- Combined: both as text — no actual file loading, no clear hierarchy

### After the fix
```
[Agent: cs-engineering-lead]
You are a senior engineering lead with the following instructions:
{agent .md content (personality, tools, rules)}

[Active Skills: aeo, landing]
Use these skill instructions as reference:
=== Skill: aeo ===
{SKILL.md content (methodology, rules)}

=== Skill: landing ===
{SKILL.md content (methodology, rules)}

[User Request]
{actual task}
```

The agent understands: "I am this persona. I have these reference materials. Here is my task."

## Inventory

### 33 Agents (personas with tools)
Engineering: cs-engineering-lead, cs-backend-engineer, cs-frontend-engineer, cs-fullstack-engineer, cs-senior-engineer, devops-engineer, startup-cto, cs-karpathy-reviewer
Product: cs-product-manager, cs-product-strategist, cs-product-analyst, cs-ux-researcher, cs-agile-product-owner, product-manager
Marketing: content-strategist, cs-content-creator, cs-demand-gen-specialist, growth-marketer, cs-webinar-marketer
C-level: cs-ceo-advisor, cs-cto-advisor, cs-financial-analyst
PM: cs-project-manager
Compliance: cs-quality-regulatory
Wiki: cs-wiki-linter, cs-wiki-librarian, cs-wiki-ingestor, cs-workspace-admin
Business: cs-aeo, cs-growth-strategist
Other: solo-founder, whatsapp-responder

### 362 Skills (knowledge/instruction bundles)
Engineering (170+): code-reviewer, senior-frontend, senior-backend, senior-fullstack, senior-devops, senior-ml-engineer, senior-qa, api-design-reviewer, database-designer, ci-cd-pipeline-builder, observability-designer, etc.
Marketing (80+): aeo, seo-audit, content-production, cold-email, email-sequence, landing, copywriting, content-strategy, page-cro, signup-flow-cro, social-content, etc.
Business (40+): sales-engineer, customer-success-manager, revenue-operations, financial-analyst, etc.
Security (15+): ai-security, cloud-security, incident-response, red-team, threat-detection, etc.
Design (10+): epic-design, ux-researcher-designer, ui-design-system, brand-guidelines, etc.
Product (10+): product-manager-toolkit, scrum-master, experiment-designer, etc.
Other (20+): lllm-cost-optimizer, rag-architect, senior-prompt-engineer, etc.

## UI Labels

| Current | Better Label | Explanation |
|---------|-------------|-------------|
| Agents | **Persona** | Who executes the task |
| Skills | **Knowledge** | What methodology/reference to apply |
| @agent | Active Persona | Shown as a badge |
| $skill | Active Knowledge | Shown as multiple badges |
