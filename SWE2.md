# SWE2 — Phase 2: WhatsApp Bot & End-to-End Automation

## Objective

Build a WhatsApp bot that bridges WhatsApp messages to opencode, allowing the user to control their MacBook remotely via WhatsApp.

## Architecture

```
WhatsApp User
    │
    ▼
┌─────────────────────┐
│  WhatsApp Bot        │
│  (Python/Node)       │
│  - whatsapp-web.js   │
│  - Command parser     │
│  - Session manager    │
└──────────┬──────────┘
           │ IPC / localhost
           ▼
┌─────────────────────┐
│  opencode CLI        │
│  - Run with model    │
│  - Skills context    │
│  - MCP tools         │
└──────────┬──────────┘
           │ result
           ▼
┌─────────────────────┐
│  Response Formatter  │
│  - Strip markdown    │
│  - Truncate long     │
│  - Format for chat   │
└─────────────────────┘
```

## Task List

### Task 2.1: Setup WhatsApp Bridge

**Option A: whatsapp-web.js (Recommended)**
```bash
npm install whatsapp-web.js qrcode-terminal
```

- Uses WhatsApp Web protocol
- Requires QR scan once (persists session)
- Can run headless
- Handles reconnection

**Option B: WhatsApp Business API**
- Requires Meta business account
- More reliable but more setup
- Not recommended for local dev

**Implementation:**
```javascript
// whatsapp-bridge.js
const { Client, LocalAuth } = require('whatsapp-web.js');

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { headless: true }
});

client.on('message', async (msg) => {
    const command = msg.body;
    const response = await executeOpenCode(command);
    msg.reply(response);
});
```

### Task 2.2: opencode CLI Wrapper

Create a wrapper that:
1. Accepts text command
2. Runs opencode with specified model
3. Captures output
4. Returns response

```python
# opencode_wrapper.py
import subprocess
import json
import tempfile

def run_opencode(command: str, model: str = "ollama/qwen2.5-coder:7b") -> str:
    """Run opencode with a command and return the response text."""
    with tempfile.NamedTemporaryFile(suffix='.md', mode='w') as f:
        f.write(f"# Task\n{command}\n")
        f.flush()
        result = subprocess.run(
            ["opencode", "run", "--model", model, command],
            capture_output=True, text=True, timeout=120
        )
        return result.stdout or result.stderr
```

### Task 2.3: Command Parser & Router

Parse incoming WhatsApp messages to determine intent:

| Command Pattern | Action | Model |
|----------------|--------|-------|
| `code: <task>` | Write/analyze code | `qwen2.5-coder:7b` |
| `explain: <topic>` | General explanation | `qwen3.5:4b-instruct` |
| `reason: <problem>` | Complex reasoning | `qwen3.5:9b-instruct` |
| `shell: <command>` | Run shell command | System (no LLM) |
| `file: <path>` | Read/write file | System (no LLM) |
| `search: <query>` | File search | System (no LLM) |
| `status` | System status | System (no LLM) |

### Task 2.4: System Action Skills

Create opencode skills for system-level actions:

**macos-control skill:**
- Launch/kill applications
- Run AppleScript
- Control windows
- Get system info
- File operations
- Clipboard operations

**development skill:**
- Git operations
- Project scaffolding
- Code review
- Test running
- Build/deploy

**media skill:**
- Screenshot capture
- Screen recording
- Audio recording
- Play/stop media

### Task 2.5: Response Formatting

WhatsApp has message length limits (~64K for text). Format responses:

1. **Short answers** (< 1000 chars): Send directly
2. **Medium answers** (1000-10000 chars): Truncate with "..." and offer "Read more" option
3. **Code blocks**: Format with ``` for WhatsApp readability
4. **Errors**: Plain text with error code

### Task 2.6: Session & State Management

Maintain conversation context:

```python
# Simple session store
sessions = {
    "user_phone": {
        "history": [...],
        "current_model": "ollama/qwen2.5-coder:7b",
        "last_command": "...",
        "context_files": [...]
    }
}
```

### Task 2.7: MacBook Power Management

Prevent sleep during operation:

```bash
# Keep MacBook awake
caffeinate -dimsu -t 3600 &

# Or use a launchd plist
# ~/Library/LaunchAgents/com.user.keepawake.plist
```

## Verification Checklist

- [ ] WhatsApp bot receives messages
- [ ] Commands are parsed and routed correctly
- [ ] opencode executes tasks with correct model
- [ ] Responses are formatted and sent back
- [ ] Code generation tasks produce valid code
- [ ] Shell commands execute and return output
- [ ] File operations work (read/write/search)
- [ ] Session history is maintained
- [ ] MacBook stays awake during operations
- [ ] Auto-reconnect on connection loss
- [ ] Error handling for long-running tasks

## Future Enhancements (Post-SWE2)

| Feature | Description |
|---------|-------------|
| Voice messages | Transcribe audio to text for commands |
| Image analysis | Send screenshots, get descriptions |
| Scheduled tasks | "Remind me at 3pm to..." |
| Multi-user | Support multiple authorized phone numbers |
| Status page | Web dashboard for system status |
| Backup/restore | Automated config backup to GitHub |
