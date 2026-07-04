# Task Execution Workflow

## Agent Lifecycle

```
User Input → Architect Agent
  → Creates GitHub Issue + adds to Project Board
  → Issue appears in "Backlog"

Task Agent picks up task
  → Moves to "In Progress"
  → Reads issue for details
  → Executes using tools (shell, filesystem, git)
  → Creates execution report
  → Creates branch/PR if code changes
  → Moves to "Done"
```

## Step-by-Step

1. **User Input:** User provides high-level requirement (via web UI or opencode TUI)
2. **Architect Agent (Persona 1):**
   - Analyzes input and decomposes into tasks
   - Creates SYS/SWE .md requirement documents
   - Creates GitHub Issues with labels (phase, persona, priority)
   - Issue auto-appears in Project Board "Backlog"
3. **Task Discovery:**
   - Agent queries GitHub Project for "To Do" items matching its persona
   - Selects highest-priority item
   - Moves item to "In Progress"
4. **Execution:**
   - Agent reads issue body for task details
   - Executes task using available MCP tools
   - Creates execution report documenting what was done
5. **Completion:**
   - If code changed: creates branch + pushes to GitHub, creates PR
   - Comments on issue with summary
   - Moves item to "Done" on project board

## Branch Naming Convention
- `swe<phase>.<task>-<description>` (e.g., `swe1.2-modelfile-attempt`)
- Each task on its own branch for traceability

## Report Format
Execution reports go in `reports/` directory:
- `reports/swe<phase>.<task>-execution-report.md`
- Contains: Status, what was done, test results, decisions made
