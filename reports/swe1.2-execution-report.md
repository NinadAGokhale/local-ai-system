# SWE1.2 Execution Report: Non-thinking Modelfile for Qwen 3.5

## Status:  CANCELLED (Not needed)

## What was attempted
1. Extracted blob paths for qwen3.5:4b and qwen3.5:9b via `ollama show`
2. Created `Modelfile.qwen3.5-4b-instruct` and `Modelfile.qwen3.5-9b-instruct` omitting `RENDERER` and `PARSER` directives
3. Created models via `ollama create`
4. Tested via API (both `/v1/chat/completions` and `/api/generate`)

## Result
- Models created but **crashed/timeout** on inference
- Root cause: Without `RENDERER qwen3.5` / `PARSER qwen3.5`, Ollama can't properly format the chat template for Qwen 3.5 architecture
- The `TEMPLATE {{ .Prompt }}` is insufficient — RENDERER/PARSER handle chat formatting internally

## Decision
- **Not needed** because **SWE1.1** already fixed the reasoning leak via `streaming: false` at the provider level
- The original `qwen3.5:4b` and `qwen3.5:9b` models work correctly with opencode now
- Non-thinking variants only needed if running with streaming=true (not our use case)
- Models were deleted: `ollama rm qwen3.5:4b-instruct qwen3.5:9b-instruct`

## Files created
- `Modelfile.qwen3.5-4b-instruct` — kept for reference (non-functional without RENDERER/PARSER)
- `Modelfile.qwen3.5-9b-instruct` — kept for reference

## Recommendation
Use original `qwen3.5:4b` and `qwen3.5:9b` with `streaming: false` in opencode config — no Modelfile needed.
