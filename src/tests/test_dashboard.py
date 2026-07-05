"""Tests for dashboard.py API endpoints."""

import json
import sys
from unittest.mock import patch, MagicMock
sys.path.insert(0, '.')

from src.web import dashboard
from src.core.config import LOG_DIR


def test_index_returns_html():
    client = dashboard.app.test_client()
    with client.session_transaction() as sess:
        sess["logged_in"] = True
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Saratthya" in resp.data


def test_login_success():
    client = dashboard.app.test_client()
    resp = client.post("/login", json={"username": "saee", "password": "saee123"})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["ok"] is True


def test_login_failure():
    client = dashboard.app.test_client()
    resp = client.post("/login", json={"username": "saee", "password": "wrong"})
    assert resp.status_code == 401


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
    assert isinstance(data["os"], str)


@patch("src.web.dashboard.subprocess.check_output")
@patch("src.web.dashboard.subprocess.run")
def test_api_status_bridge_disabled(mock_run, mock_check):
    mock_check.return_value = b"up 3 days"
    mock_run.side_effect = lambda *a, **kw: MagicMock(stdout='{"models":[{}]}')

    client = dashboard.app.test_client()
    resp = client.get("/api/status")
    assert resp.status_code == 200


def test_api_history_logs_url_logged():
    client = dashboard.app.test_client()
    resp = client.get("/api/logs?limit=5&phone=+14088008935")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)


def test_api_chat_missing_message():
    client = dashboard.app.test_client()
    resp = client.post("/api/chat", json={})
    assert resp.status_code == 400
    data = json.loads(resp.data)
    assert "error" in data


def test_api_set_agent():
    client = dashboard.app.test_client()
    resp = client.post("/api/agent", json={"agent": "cto"})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["ok"] is True
    assert data["current_agent"] == "cto"


def test_api_set_skill():
    client = dashboard.app.test_client()
    resp = client.post("/api/skill", json={"skill": "content-production"})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["ok"] is True
    assert data["current_skill"] == "content-production"


def test_api_clear_agent():
    client = dashboard.app.test_client()
    resp = client.post("/api/agent", json={"agent": None})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["current_agent"] is None


def test_api_clear_skill():
    client = dashboard.app.test_client()
    resp = client.post("/api/skill", json={"skill": None})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["current_skill"] is None


def test_api_models_has_keys():
    client = dashboard.app.test_client()
    resp = client.get("/api/models")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "ollama_models" in data
    assert "opencode_models" in data


def test_api_agents_returns_list():
    client = dashboard.app.test_client()
    resp = client.get("/api/agents")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "agents" in data
    assert isinstance(data["agents"], list)


def test_api_skills_returns_list():
    client = dashboard.app.test_client()
    resp = client.get("/api/skills")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "skills" in data
    assert isinstance(data["skills"], list)


def test_api_chat_new():
    client = dashboard.app.test_client()
    resp = client.post("/api/chat/new", json={"phone": "web-ui"})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "ok"


def test_api_conversations():
    client = dashboard.app.test_client()
    resp = client.get("/api/conversations")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)


def test_dashboard_html_has_autocomplete_js():
    """Regression: @/$ autocomplete must be wired through both keydown + input."""
    with open("src/web/templates/dashboard.html") as f:
        html = f.read()

    # keydown handler must set _pendingACTag for @ and $
    assert "e.key === '@'" in html
    assert "e.key === '$'" in html
    assert "_pendingACTag = 'agent'" in html
    assert "_pendingACTag = 'skill'" in html

    # input handler must consume the flag
    assert "if (_pendingACTag)" in html
    assert 'showAC(_pendingACTag)' in html
    assert "_pendingACTag = null" in html

    # fallback: InputEvent.data
    assert "e.data === '@'" in html
    assert "e.data === '$'" in html

    # last resort: cursor-1 check
    assert "prevChar === '@'" in html
    assert "prevChar === '$'" in html

    # modifiers MUST NOT block @/$ (they require Shift on US keyboards)
    func_start = html.find("function onInputKey")
    func_end = html.find("        }", func_start + 200)
    func_body = html[func_start:func_end]
    assert "!e.shiftKey" not in func_body, \
        "onInputKey must not filter by shiftKey — @ and $ require Shift"
