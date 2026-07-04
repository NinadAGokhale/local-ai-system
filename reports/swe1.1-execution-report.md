# SWE1.1 Execution Report: Verify provider-level streaming: false

## Status: ✅ Completed

## Test Results

| Test | Result | Notes |
|------|--------|-------|
| API: qwen3.5:4b with stream:false | ✅ content="Hi", reasoning present separately | Non-streaming returns both fields |
| API: qwen3.5:4b with stream:true | ⚠️ First chunk has empty content, only reasoning | Root cause confirmed |
| opencode run: qwen3.5:4b | ✅ Output: "Hello" — clean, no reasoning leak | streaming:false in config works |
| opencode run: qwen3.5:9b | ✅ Output: "hello" — clean, no reasoning leak | streaming:false in config works |

## Conclusion
The `streaming: false` provider-level setting in `opencode.jsonc` **does fix** the Qwen 3.5 reasoning leak issue. The `simulateStreamingMiddleware` correctly extracts only the `content` field from the non-streaming response.

## Action
No further changes needed. Both `qwen3.5:4b` and `qwen3.5:9b` are usable with opencode.
