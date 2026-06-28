# SWE3 — Agent Architecture & GitHub Project Management Integration

## Objective

Set up the project management layer: GitHub Projects board + GitHub MCP Server in opencode, enabling agents to autonomously create, assign, and execute tasks from the project board.

## Prerequisites

- GitHub account (free)
- GitHub Personal Access Token with `repo`, `project`, `issues` scopes
- opencode 1.17.11 configured (already done)

## Task List

### Task 3.1: GitHub Account & Token Setup

**User action:**

1. Create GitHub account at https://github.com/signup (if none)
2. Create Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Scopes: `repo` (full control), `project` (Projects access), `write:org` (if using org projects)
   - Copy the token immediately
3. Add to shell profile (`~/.zshrc`):
   ```bash
   export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
   ```
4. Reload: `source ~/.zshrc`

### Task 3.2: Create GitHub Repository & Project Board

**Steps:**

```bash
# 1. Create repo via gh CLI (or manually on GitHub)
gh repo create local-ai-system --public --description "Local AI System - WhatsApp-controlled MacBook automation" --clone

# Or create on github.com first, then:
cd ~/Desktop/local-ai-system
git remote add origin https://github.com/YOUR_USERNAME/local-ai-system.git
git push -u origin main
```

**2. Create GitHub Project (Projects v2):**
- On github.com, go to your repo
- Click "Projects" → "Create project"
- Choose "Board" template
- Name: "Local AI System"
- Customize fields:
  - Status: Backlog, To Do, In Progress, Review, Done (Board columns)
  - Phase: SWE0, SWE1, SWE2, SWE3 (Single select)
  - Persona: Architect, Coding, System, DevOps, Bridge (Single select)
  - Priority: P0, P1, P2 (Single select)

**3. Create initial issues from existing design docs:**
```bash
# Create issues for each SWE phase
gh issue create --title "SWE0: GitHub + opencode MCP Setup" --body "See SWE3.md for details" --label "phase:swe0"
gh issue create --title "SWE1: Local Model Setup & opencode Integration" --body "See SWE1.md" --label "phase:swe1"
gh issue create --title "SWE2: WhatsApp Bot & E2E Automation" --body "See SWE2.md" --label "phase:swe2"
gh issue create --title "SWE3: Agent Architecture & Project Automation" --body "See SWE3.md" --label "phase:swe3"
```

### Task 3.3: Configure GitHub MCP Server in opencode

**Edit `~/.config/opencode/opencode.jsonc`:**

```jsonc
{
  "mcp": {
    "github": {
      "type": "remote",
      "command": ["npx", "@github/github-mcp-server"],
      "enabled": true,
      "environment": {
        "GITHUB_TOKEN": "{env:GITHUB_TOKEN}"
      }
    }
  }
}
```

**Alternative: Remote GitHub MCP (no local process):**

```jsonc
{
  "mcp": {
    "github": {
      "type": "remote",
      "command": [],
      "url": "https://api.githubcopilot.com/mcp/",
      "enabled": true,
      "oauth": false,
      "headers": {
        "Authorization": "Bearer {env:GITHUB_TOKEN}",
        "User-Agent": "opencode/1.17.11"
      }
    }
  }
}
```

**Verify:**
```bash
opencode mcp list
# Should show "github" as connected
opencode mcp debug github
# Should show auth status
```

### Task 3.4: Create Architect Agent (Persona 1)

The Architect Agent takes high-level user input and:
1. Creates SYS/SWE requirement documents
2. Breaks requirements into GitHub Issues
3. Adds issues to the GitHub Project Board
4. Sets correct labels (phase, persona, priority)

**Implementation approach:**

The Architect Agent is an opencode **skill** + **agent configuration**:

**Skill file: `~/.config/opencode/skills/architect-agent.md`:**
```markdown
---
name: architect-agent
description: System architect that creates requirements and project tasks
---

You are the Architect Agent. Your role:

1. When given a high-level user requirement:
   a. Analyze and decompose into clear requirements
   b. Create SYS.md (system requirements) and SWE.md (implementation tasks)
   c. Create GitHub Issues for each task
   d. Add issues to the GitHub Project Board with correct metadata

2. When reviewing existing tasks:
   a. Check GitHub Project Board for inconsistencies
   b. Ensure issues have correct phase/persona/priority labels
   c. Suggest rebalancing if one persona is overloaded

You have access to:
- GitHub MCP tools (issues, projects)
- Filesystem MCP (for reading/writing .md files)
- Shell MCP (for git operations)
```

### Task 3.5: Create Specialized Task Agents

Each task agent is a combination of:
- An opencode **agent** definition
- A **skill file** with instructions
- **MCP tool access** scoped to their persona

**Persona 2: Coding Agent**
- Model: `ollama/qwen2.5-coder:7b`
- MCP: GitHub, Filesystem, Shell
- Skill: coding-agent.md
- Handles: Implementation, code review, testing

**Persona 3: System Agent**
- Model: `ollama/qwen3.5:4b-instruct`
- MCP: Shell, Filesystem, macOS automation
- Skill: system-agent.md
- Handles: macOS operations, config management, file ops

**Persona 4: DevOps Agent**
- Model: `ollama/qwen3.5:4b-instruct`
- MCP: GitHub (Actions), Shell
- Skill: devops-agent.md
- Handles: CI/CD, git operations, deployment

**Persona 5: WhatsApp Bridge Agent**
- Model: `ollama/qwen3.5:4b-instruct`
- MCP: WhatsApp (custom), opencode CLI
- Skill: whatsapp-bridge.md
- Handles: Message parsing, response formatting

### Task 3.6: Task Execution Workflow

When an agent picks up a task from the GitHub board:

```
1. AGENT: Query GitHub Project for "To Do" items with matching persona
   → GitHub MCP: project_items_read(status:"To Do", persona:"Coding")

2. AGENT: Select highest-priority item
   → Move item to "In Progress"
   → GitHub MCP: project_item_update(id:X, status:"In Progress")

3. AGENT: Read issue body for task details
   → GitHub MCP: issues_read(issue_number:N)

4. AGENT: Execute the task using tools
   → Shell/Filesystem/Git commands as needed

5. AGENT: Report results
   → Comment on issue with summary
   → Create PR if code changes
   → Move item to "Review" or "Done"
   → GitHub MCP: issue_comment_create(...)
   → GitHub MCP: project_item_update(id:X, status:"Done")
```

### Task 3.7: MCP Tool Scoping Per Persona

Configure which MCP tools each agent persona can access to limit context usage:

```jsonc
// In opencode.jsonc agent configuration
{
  "agent": {
    "coding": {
      "tools": {
        "github_issues_*": true,
        "github_pull_requests_*": true,
        "filesystem_*": true,
        "shell_*": true
      }
    },
    "system": {
      "tools": {
        "filesystem_*": true,
        "shell_*": true,
        "github_issues_read": true
      }
    },
    "architect": {
      "tools": {
        "github_*": true,
        "filesystem_write": true
      }
    }
  }
}
```

### Task 3.8: Automation Script — Project Sync

Optional helper script that syncs local .md files to GitHub Issues:

```bash
#!/bin/bash
# sync-swe-to-github.sh
# Reads SWE*.md files and creates/updates GitHub Issues

for f in SWE*.md; do
  phase=$(echo $f | sed 's/\.md//')
  title=$(head -1 "$f" | sed 's/^# //')
  body=$(cat "$f")
  
  # Create or update issue
  gh issue create --title "$title" --body "$body" --label "phase:${phase,,}"
done
```

## Verification Checklist

- [ ] GitHub account created
- [ ] GitHub PAT generated with correct scopes
- [ ] Repository created and design docs pushed
- [ ] GitHub Project board created with correct columns/fields
- [ ] opencode MCP config updated with GitHub server
- [ ] `opencode mcp list` shows GitHub connected
- [ ] Initial issues created from SWE docs
- [ ] Architect Agent skill created
- [ ] Task agent skills created
- [ ] MCP tool scoping configured per persona
- [ ] Agent can query GitHub Project board
- [ ] Agent can move items between columns
- [ ] Agent can create issues from skills

## Credentials Needed

| Item | Required From User |
|------|-------------------|
| GitHub username | You tell me |
| GitHub PAT (classic) | Create at https://github.com/settings/tokens with `repo`, `project`, `issues` scopes |
| GitHub repo name | `local-ai-system` (suggested) |
| GitHub Project number | Auto-assigned when project is created |
