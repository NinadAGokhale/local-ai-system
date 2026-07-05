"""Tests for core/config.py"""

import sys
import os
sys.path.insert(0, '.')

from src.core.config import PROJECT_ROOT, SESSION_FILE, LOG_DIR, DEFAULT_MODEL


def test_project_root_is_absolute():
    assert os.path.isabs(PROJECT_ROOT)


def test_project_root_has_src():
    src_dir = os.path.join(PROJECT_ROOT, "src")
    assert os.path.isdir(src_dir)


def test_session_file_is_absolute():
    assert os.path.isabs(SESSION_FILE)


def test_session_file_name():
    assert SESSION_FILE.endswith(".sessions.json")


def test_log_dir_is_absolute():
    assert os.path.isabs(LOG_DIR)


def test_log_dir_name():
    assert LOG_DIR.endswith("logs")


def test_default_model():
    assert DEFAULT_MODEL == "ollama/qwen2.5-coder:7b"
