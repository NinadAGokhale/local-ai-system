"""MLX server wrapper — OpenAI-compatible API running on Apple Silicon."""

import json
import os
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

MLX_HOST = os.environ.get("MLX_HOST", "http://127.0.0.1")
MLX_PORT = int(os.environ.get("MLX_PORT", "8080"))
MLX_CACHE = Path(os.path.expanduser("~/.cache/huggingface/hub"))


def _mlx_url(path: str) -> str:
    return f"{MLX_HOST}:{MLX_PORT}{path}"


def is_server_running() -> bool:
    """Check if MLX server is responding."""
    try:
        req = urllib.request.Request(_mlx_url("/v1/models"))
        resp = urllib.request.urlopen(req, timeout=2)
        return resp.status == 200
    except Exception:
        return False


def get_active_model() -> Optional[str]:
    """Get the model currently loaded on the MLX server."""
    try:
        req = urllib.request.Request(_mlx_url("/v1/models"))
        resp = urllib.request.urlopen(req, timeout=2)
        data = json.loads(resp.read().decode())
        models = data.get("data", [])
        if models:
            return models[0].get("id", "")
    except Exception:
        pass
    return None


def list_cached_models() -> list[str]:
    """List MLX models fully cached in HuggingFace hub."""
    if not MLX_CACHE.exists():
        return []
    models = []
    for d in sorted(MLX_CACHE.glob("models--mlx-community--*")):
        name = d.name.replace("models--mlx-community--", "").replace("--", "/")
        safetensors = list(d.rglob("*.safetensors"))
        if safetensors:
            models.append(name)
    return models


def build_mlx_model_id(repo_id: str) -> str:
    """Convert HF repo ID to a short mlx model key.
    e.g. 'mlx-community/Llama-3.1-8B-Instruct-4bit' -> 'mlx/Llama-3.1-8B-Instruct-4bit'
    """
    short = repo_id.split("/", 1)[-1] if "/" in repo_id else repo_id
    return f"mlx/{short}"


def parse_mlx_model_id(model_id: str) -> Optional[str]:
    """Convert 'mlx/Llama-3.1-8B-Instruct-4bit' back to HF repo ID.
    Returns None if not an mlx model.
    """
    if not model_id.startswith("mlx/"):
        return None
    short = model_id[len("mlx/"):]
    return f"mlx-community/{short}"


MODEL_META: dict[str, dict] = {
    # --- Ollama models ---
    "qwen3.5:latest": {
        "emoji": "🧠",
        "label": "Qwen 3.5",
        "desc": "Best all-round — chat, analysis, reasoning",
    },
    "qwen3.5:9b": {
        "emoji": "🧠",
        "label": "Qwen 3.5 9B",
        "desc": "Large reasoning model for complex analysis",
    },
    "qwen3.5:4b": {
        "emoji": "⚡",
        "label": "Qwen 3.5 4B",
        "desc": "Fast lightweight — best for quick responses",
    },
    "qwen3.5:4b-chat": {
        "emoji": "⚡",
        "label": "Qwen 3.5 4B Chat",
        "desc": "Fast chat-optimized model",
    },
    "qwen2.5-coder:7b": {
        "emoji": "📝",
        "label": "Qwen Coder 7B",
        "desc": "Best for code generation and programming",
    },
    "llama3.1:8b": {
        "emoji": "🌐",
        "label": "Llama 3.1 8B",
        "desc": "Strong general-purpose by Meta",
    },
    "llama3.2:3b": {
        "emoji": "⚡",
        "label": "Llama 3.2 3B",
        "desc": "Ultra-fast for simple tasks",
    },
    "mistral:7b": {
        "emoji": "🌐",
        "label": "Mistral 7B",
        "desc": "Efficient general-purpose model",
    },
    "phi4-mini:3.8b": {
        "emoji": "⚡",
        "label": "Phi-4 Mini 3.8B",
        "desc": "Microsoft's compact efficient model",
    },
    "deepseek-r1:8b": {
        "emoji": "🧠",
        "label": "DeepSeek R1 8B",
        "desc": "Reasoning-focused for complex problems",
    },
    # --- MLX models (short names, after mlx/ prefix) ---
    "Llama-3.1-8B-Instruct-4bit": {
        "emoji": "🌐",
        "label": "Llama 3.1 8B (MLX)",
        "desc": "4-bit quantized for Apple Silicon",
    },
    "Mistral-7B-Instruct-v0.3-4bit": {
        "emoji": "🌐",
        "label": "Mistral 7B (MLX)",
        "desc": "4-bit quantized Mistral",
    },
    "DeepSeek-R1-Distill-Qwen-7B-4bit": {
        "emoji": "🧠",
        "label": "DeepSeek R1 7B (MLX)",
        "desc": "Reasoning model for Apple Silicon",
    },
    "Phi-4-mini-instruct-4bit": {
        "emoji": "⚡",
        "label": "Phi-4 Mini (MLX)",
        "desc": "Microsoft's compact model for Apple Silicon",
    },
    "Llama-3.2-3B-Instruct-4bit": {
        "emoji": "⚡",
        "label": "Llama 3.2 3B (MLX)",
        "desc": "Ultra-fast, efficient on Apple Silicon",
    },
    "Qwen3.5-9B-MLX-4bit": {
        "emoji": "🧠",
        "label": "Qwen 3.5 9B (MLX)",
        "desc": "Large reasoning for Apple Silicon",
    },
    "Qwen3.5-4B-MLX-4bit": {
        "emoji": "⚡",
        "label": "Qwen 3.5 4B (MLX)",
        "desc": "Fast lightweight for Apple Silicon",
    },
    "Qwen2.5-Coder-7B-Instruct-4bit": {
        "emoji": "📝",
        "label": "Qwen Coder 7B (MLX)",
        "desc": "Code generation for Apple Silicon",
    },
}


def get_model_meta(model_id: str) -> dict:
    """Get emoji + description for any model ID (ollama/, mlx/, or bare)."""
    # Strip provider prefix
    for prefix in ("ollama/", "mlx/", "opencode/"):
        if model_id.startswith(prefix):
            model_id = model_id[len(prefix):]
            break
    meta = MODEL_META.get(model_id, {})
    if not meta:
        return {"emoji": "🤖", "label": model_id, "desc": ""}
    return meta
