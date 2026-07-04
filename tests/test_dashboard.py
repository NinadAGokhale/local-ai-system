"""Tests for dashboard.py API endpoints."""

import json
import sys
from unittest.mock import patch, MagicMock
sys.path.insert(0, '.')

import dashboard
from message_logger import MESSAGES_LOG, REQUIREMENTS_LOG


def test_index_returns_html():
    client = dashboard.app.test_client()
    with client.session_transaction() as sess:
        sess["logged_in"] = True
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Saratthya" in resp.data


def test_api_logs_empty():
    client = dashboard.app.test_client()
    resp = client.get("/api/logs")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)


def test_api_requirements_empty():
    client = dashboard.app.test_client()
    resp = client.get("/api/requirements")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)


def test_api_status_keys():
    client = dashboard.app.test_client()
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "ollama_models" in data
    assert "messages_logged" in data
    assert "sessions_active" in data
    assert "bridge_online" in data
    assert "os" in data
    assert "host" in data
    assert "uptime" in data


def test_api_status_types():
    client = dashboard.app.test_client()
    resp = client.get("/api/status")
    data = json.loads(resp.data)
    assert isinstance(data["ollama_models"], int)
    assert isinstance(data["messages_logged"], int)
    assert isinstance(data["sessions_active"], int)
    assert isinstance(data["bridge_online"], bool)
    assert isinstance(data["os"], str)


@patch("dashboard.subprocess.check_output")
@patch("dashboard.subprocess.run")
def test_api_status_bridge_disabled(mock_run, mock_check):
    mock_check.return_value = b"up 3 days"
    mock_run.side_effect = lambda *a, **kw: MagicMock(stdout='{"models":[{}]}')

    client = dashboard.app.test_client()
    resp = client.get("/api/status")
    data = json.loads(resp.data)
    assert data["bridge_online"] is False


def test_api_history_logs_url_logged():
    client = dashboard.app.test_client()
    resp = client.get("/api/logs?limit=5&phone=+14088008935")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)
