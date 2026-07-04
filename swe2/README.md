# SWE2 — WhatsApp Bot Bridge

## Files

| File | Purpose |
|------|---------|
| `whatsapp-bridge.js` | WhatsApp Web client using whatsapp-web.js |
| `opencode_wrapper.py` | CLI wrapper to call opencode from Python |
| `command_parser.py` | Parse WhatsApp messages to determine intent and route |
| `response_formatter.py` | Format opencode output for WhatsApp display |
| `session_manager.py` | Session/state management per user |
| `main.py` | Main entry point tying everything together |
| `power_manager.sh` | Keep MacBook awake during operation |
| `package.json` | Node.js dependencies |
| `requirements.txt` | Python dependencies (none beyond stdlib) |

## Usage

### Start WhatsApp Bridge (Node.js)
```bash
cd swe2
npm install
node whatsapp-bridge.js
# Scan QR code with WhatsApp
```

### Test Python components standalone
```bash
python main.py "+1234567890" "status"
python main.py "+1234567890" "code: write fibonacci in python"
python main.py "+1234567890" "explain: what is machine learning"
```

### Power Management
```bash
./power_manager.sh start   # prevent sleep
./power_manager.sh status  # check status
./power_manager.sh stop    # allow sleep
```

## Dependencies
- Node.js: `whatsapp-web.js`, `qrcode-terminal`
- Python: stdlib only
- System: opencode CLI, puppeteer (installed by whatsapp-web.js)
