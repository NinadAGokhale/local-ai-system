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
| `qwen3.5:4b` | 3.4 GB | ✅ Fixed (streaming:false) | Lightweight reasoning |
| `qwen3.5:9b` | 6.6 GB | ✅ Fixed (streaming:false) | Complex reasoning |

## Project Structure

```
local-ai-system/
├── README.md              # This file
├── SYS1.md                # System Requirements & Architecture
├── SYS2.md                # Technical Design & Implementation Plan
├── SWE1.md                # Phase 1: Local Model Setup & opencode Integration
├── SWE2.md                # Phase 2: WhatsApp Bot & End-to-End Automation
├── SWE3.md                # Phase 3: Agent Architecture & Project Automation
├── swe2/                  # WhatsApp bot code (Python + Node.js)
├── swe3/                  # Agent skills, workflow, MCP scoping
├── skills/                # opencode skill files (reference copy)
├── reports/               # Execution reports for each task
├── Modelfile.*            # Reference Modelfiles
└── .gitignore
```

## Phases

| Phase | Description | Status |
|-------|-------------|--------|
| SWE1 | Local model setup + opencode integration | ✅ Complete |
| SWE2 | WhatsApp bot + end-to-end automation | ✅ Complete |
| SWE3 | Agent architecture + project automation | ✅ Complete |

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

## GitHub

- **Issues/Board:** https://github.com/NinadAGokhale/local-ai-system/projects/1
- **Branch:** `dev` for development, feature branches for individual tasks

## Key Decisions

- **Local-first:** All AI inference runs on-device
- **No cloud deps:** No OpenAI/Anthropic API keys needed
- **streaming:false:** Fixes Qwen 3.5 reasoning leak at provider level
- **GitHub Projects:** Free project management with native git integration
- **MCP-native:** All integrations use MCP servers for tool access
