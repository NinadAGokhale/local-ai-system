# SWE5: MLX Server Integration + Model Provider UI

## Requirement

The dashboard needs to support three model providers:
1. **Ollama (local)** — existing, manages multiple models via `ollama list`
2. **MLX (Apple Silicon)** — new, Apple's ML framework running an OpenAI-compatible server
3. **Opencode (cloud)** — existing, cloud-hosted models via opencode CLI

Non-technical users need to understand which model to pick — add emoji categories
and tooltip descriptions. Only show models that are actually available on each
provider.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Dashboard (Flask)                  │
│                                                       │
│  /api/models                                          │
│    ├── ollama list (subprocess) → ollama_models[]     │
│    ├── mlx_wrapper.list_cached_models() → mlx_models[]│
│    └── hardcoded → opencode_models[]                  │
│                                                       │
│  Model routing (opencode_wrapper.run_opencode):        │
│    ollama/*  → run_ollama()   → Ollama REST API       │
│    mlx/*     → run_mlx()      → MLX OpenAI-compat API │
│    opencode/* → run_opencode_cli() → opencode CLI     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                    MLX Server                          │
│  python -m mlx_lm.server --model <repo_id>             │
│  Default: http://127.0.0.1:8080                        │
│  Configurable: MLX_HOST + MLX_PORT env vars            │
│  API: /v1/chat/completions (OpenAI-compatible)         │
│                                                        │
│  Only loads ONE model at a time.                        │
│  Cached models: ~/.cache/huggingface/hub/models--*     │
└──────────────────────────────────────────────────────┘
```

### MLX Wrapper (`src/core/mlx_wrapper.py`)

| Function | Purpose |
|----------|---------|
| `is_server_running()` | Health check via `GET /v1/models` |
| `get_active_model()` | Get the model ID loaded on the server |
| `list_cached_models()` | Scan HuggingFace cache for fully downloaded MLX models |
| `get_model_meta(id)` | Return emoji + label + description for any model |

### Model Metadata

Every model gets an emoji category + short description so non-technical users
can pick the right one:

| Emoji | Category | When to use |
|-------|----------|-------------|
| 🧠 | Reasoning | Complex analysis, logic, deep thinking |
| ⚡ | Fast | Quick responses, simple tasks, chat |
| 🌐 | General | Balanced all-purpose model |
| 📝 | Code | Code generation, programming tasks |
| 🤖 | Default | Fallback for unrecognized models |

## Changes

### New file: `src/core/mlx_wrapper.py`
- MLX server health check, model listing, API calling
- `MODEL_META` dict with emoji + descriptions for all known models
- `get_model_meta()` resolves emoji for any model ID prefix

### Changed: `src/core/opencode_wrapper.py`
- `run_opencode()` now routes `mlx/*` prefix to `run_mlx()`
- New `run_mlx()` function calls `POST /v1/chat/completions`
- `_strip_prefix()` handles `mlx/` prefix

### Changed: `src/web/dashboard.py`
- `/api/models` returns `mlx_models[]` with `{id, name, emoji, desc}`
- MLX models come from scanning huggingface cache

### Changed: `src/web/templates/dashboard.html`
- `loadModels()` renders three optgroups: Ollama, MLX, Opencode
- Each option has emoji prefix + `title` attribute for tooltip
- MLX group shows "No MLX models cached" message when empty

### Config
- `MLX_HOST` env var (default: `http://127.0.0.1`)
- `MLX_PORT` env var (default: `8080`)
- `src/web/.env.example` updated with MLX defaults

## Limitations

- MLX server loads ONE model at a time (unlike Ollama which manages a pool).
  To switch models, restart the MLX server with a different `--model`.
- Only cached models (fully downloaded) appear in the dropdown.
  Run `python -m mlx_lm.server --model <id>` to trigger download.
