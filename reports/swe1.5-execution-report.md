# SWE1.5 Execution Report: Test all models end-to-end

## Status: ✅ Completed

## Test Matrix

| Model | Test | Result | Output |
|-------|------|--------|--------|
| `qwen2.5-coder:7b` | "write a python function to add two numbers" | ✅ | Correct code output |
| `qwen3.5:4b` | "explain what is AI in one sentence" | ✅ | Clean text, no reasoning leak |
| `qwen3.5:9b` | "debug: why is my python list index out of range" | ✅ | Helpful debugging response |

## Verification Checklist
- [x] `opencode` launches without errors
- [x] `/model ollama/qwen2.5-coder:7b` shows responses correctly
- [x] `/model ollama/qwen3.5:4b` shows responses (no reasoning leak)
- [x] `/model ollama/qwen3.5:9b` shows responses (no reasoning leak)
- [x] Skills are loaded and accessible (4 skill files created in SWE1.4)
- [x] Switching models via `/model` works mid-session
- [x] Tool calls (shell, file ops) work with local models

## Conclusion
All 3 local models work correctly with opencode. The reasoning leak issue is resolved via `streaming: false`.
