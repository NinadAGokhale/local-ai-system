# Local AI System — WhatsApp-Controlled MacBook Automation

Control your MacBook via WhatsApp using local LLMs, opencode, and custom automation.

## System Specs

- **Hardware:** MacBook Pro 14" (2021), M1 Pro, 16 GB RAM
- **OS:** macOS 26.0.1
- **LLM Server:** Ollama 0.30.10
- **AI Agent:** opencode 1.17.11

## Local Models

| Model | Size | Status | Use Case |
|-------|------|--------|----------|
| `qwen2.5-coder:7b` | 4.7 GB | ✅ Working | Primary coding tasks |
| `qwen3.5:4b` | 3.4 GB | ⚠️ Needs fix | Lightweight reasoning |
| `qwen3.5:9b` | 6.6 GB | ⚠️ Needs fix | Complex reasoning |

## Project Structure

```
local-ai-system/
├── README.md          # This file
├── SYS1.md            # System Requirements & Architecture
├── SYS2.md            # Technical Design & Implementation Plan
├── SWE1.md            # Phase 1: Local Model Setup & opencode Integration
└── SWE2.md            # Phase 2: WhatsApp Bot & End-to-End Automation
```

## Phases

| Phase | Description | Status |
|-------|-------------|--------|
| SWE1 | Local model setup + opencode integration | 📝 Planned |
| SWE2 | WhatsApp bot + end-to-end automation | 📝 Planned |

## Quick Start

```bash
# 1. Ensure Ollama is running
ollama serve

# 2. Launch opencode
opencode

# 3. Switch to local model
/model ollama/qwen2.5-coder:7b

# 4. Start working
```

## Key Decisions

- **Local-first:** All AI inference runs on-device
- **No cloud deps:** No OpenAI/Anthropic API keys needed
- **No proxy:** Config-only approach (no bash scripts)
- **Git-tracked:** All config and docs version-controlled
