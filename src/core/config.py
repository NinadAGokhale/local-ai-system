"""Central configuration — paths, constants, and defaults."""

import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')
)

SESSION_FILE = os.path.join(PROJECT_ROOT, '.sessions.json')
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

DEFAULT_MODEL = "ollama/qwen2.5-coder:7b"
