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


SPEED_FAST =  "⚡ Fast – 1-4 sec reply. Best for simple chat, greetings, quick answers."
SPEED_MED =   "🌐 General – 3-10 sec reply. Good all-rounder for everyday questions."
SPEED_SLOW =  "🧠 Thinking – 10-30 sec reply. Best for complex reasoning, math, analysis. Give it time to think."
SPEED_CODE =  "📝 Coding – 5-15 sec reply. Best for writing, explaining, or fixing code."

MODEL_META: dict[str, dict] = {
    # --- Ollama models ---
    "qwen3.5:latest":     {"emoji": "🌐", "label": "Qwen 3.5",        "desc": SPEED_MED + " Handles any question well — chat, research, analysis."},
    "qwen3.5:9b":         {"emoji": "🧠", "label": "Qwen 3.5 9B",     "desc": SPEED_SLOW + " The smartest option. Use for tough problems."},
    "qwen3.5:4b":         {"emoji": "⚡", "label": "Qwen 3.5 4B",     "desc": SPEED_FAST + " Quick and simple — good for everyday chat."},
    "qwen3.5:4b-chat":    {"emoji": "⚡", "label": "Qwen 3.5 4B Chat","desc": SPEED_FAST + " Optimized for casual conversation."},
    "qwen2.5-coder:7b":   {"emoji": "📝", "label": "Qwen Coder 7B",   "desc": SPEED_CODE + " Built for programming tasks."},
    "llama3.1:8b":        {"emoji": "🌐", "label": "Llama 3.1 8B",    "desc": SPEED_MED + " Reliable all-rounder by Meta."},
    "llama3.2:3b":        {"emoji": "⚡", "label": "Llama 3.2 3B",    "desc": SPEED_FAST + " Ultra-light model — almost instant replies."},
    "mistral:7b":         {"emoji": "🌐", "label": "Mistral 7B",      "desc": SPEED_MED + " Efficient and capable all-purpose model."},
    "phi4-mini:3.8b":     {"emoji": "⚡", "label": "Phi-4 Mini",      "desc": SPEED_FAST + " Microsoft's compact model — punchy and quick."},
    "deepseek-r1:8b":     {"emoji": "🧠", "label": "DeepSeek R1 8B",  "desc": SPEED_SLOW + " Shows its reasoning step-by-step. Great for puzzles, logic, analysis."},
    # --- MLX models (short names, after mlx/ prefix) ---
    "Llama-3.1-8B-Instruct-4bit":   {"emoji": "🌐", "label": "Llama 3.1 8B (MLX)",    "desc": SPEED_MED + " Runs on your Mac — no cloud needed."},
    "Mistral-7B-Instruct-v0.3-4bit":{"emoji": "🌐", "label": "Mistral 7B (MLX)",      "desc": SPEED_MED + " Local model, good all-round performance."},
    "DeepSeek-R1-Distill-Qwen-7B-4bit":{"emoji": "🧠", "label": "DeepSeek R1 7B (MLX)","desc": SPEED_SLOW + " Step-by-step reasoning, fully offline."},
    "Phi-4-mini-instruct-4bit":     {"emoji": "⚡", "label": "Phi-4 Mini (MLX)",       "desc": SPEED_FAST + " Microsoft's compact model on your Mac."},
    "Llama-3.2-3B-Instruct-4bit":   {"emoji": "⚡", "label": "Llama 3.2 3B (MLX)",    "desc": SPEED_FAST + " Tiny, light, instant replies — fully offline."},
    "Qwen3.5-9B-MLX-4bit":          {"emoji": "🧠", "label": "Qwen 3.5 9B (MLX)",     "desc": SPEED_SLOW + " Large reasoning model on your Mac."},
    "Qwen3.5-4B-MLX-4bit":          {"emoji": "⚡", "label": "Qwen 3.5 4B (MLX)",     "desc": SPEED_FAST + " Lightweight chat model on your Mac."},
    "Qwen2.5-Coder-7B-Instruct-4bit":{"emoji": "📝", "label": "Qwen Coder 7B (MLX)",   "desc": SPEED_CODE + " Code assistant running on your Mac."},
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
