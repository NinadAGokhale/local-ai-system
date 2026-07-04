---
name: bridge-agent
description: External connection agent — handles MCP-based integrations (reserved for future use)
---

# Bridge Agent

**Status:** Deprecated. The WhatsApp bridge has been removed in favor of a web-only architecture.

This agent was previously responsible for translating external messaging (WhatsApp) into opencode tasks. In the current architecture, the web UI at `localhost:5050` is the sole interface.

## Future Use

If an external bridge is needed in the future (e.g., WhatsApp, Telegram, Slack), it should be implemented as:
1. An MCP server in `opencode.jsonc`
2. A new agent persona with MCP tool access
3. A dedicated handler in the web UI or standalone process
