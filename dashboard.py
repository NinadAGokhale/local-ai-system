"""Web dashboard for Local AI System — logs viewer + requirement submission."""

import json
import os
import subprocess
from pathlib import Path

from flask import Flask, render_template, request, jsonify

from message_logger import get_recent_messages, get_recent_requirements, log_requirement
from command_parser import parse_command, CommandType
from session_manager import SessionManager
from main import handle_message

session_manager = SessionManager()

app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

REPO = "NinadAGokhale/local-ai-system"


@app.route("/")
def index():
    messages = get_recent_messages(limit=100)
    requirements = get_recent_requirements(limit=20)
    return render_template("dashboard.html", messages=messages, requirements=requirements)


@app.route("/api/logs")
def api_logs():
    phone = request.args.get("phone")
    limit = int(request.args.get("limit", 50))
    messages = get_recent_messages(limit=limit, phone=phone)
    return jsonify(messages)


@app.route("/api/requirements", methods=["GET"])
def api_requirements():
    return jsonify(get_recent_requirements())


@app.route("/api/requirements", methods=["POST"])
def api_create_requirement():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    phone = data.get("phone", "web-ui")
    text = data["text"]

    cmd_type, cleaned, model = parse_command(text)
    is_new_requirement = cmd_type.value == "unknown" or data.get("is_requirement", True)

    issue_url = None
    if is_new_requirement:
        issue_url = create_github_issue(text)

    log_requirement(
        phone=phone,
        requirement_text=text,
        issue_url=issue_url,
        status="created" if issue_url else "parsed",
    )

    return jsonify({
        "status": "created" if issue_url else "parsed",
        "issue_url": issue_url,
        "intent": cmd_type.value,
        "cleaned_text": cleaned,
    })


@app.route("/api/status")
def api_status():
    import platform
    uname = platform.uname()
    uptime = "N/A"
    try:
        uptime = subprocess.check_output(["uptime"]).decode().strip()
    except Exception:
        pass
    model_count = 0
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout:
            model_count = len(json.loads(result.stdout).get("models", []))
    except Exception:
        pass

    log_dir = Path(__file__).parent / "logs"
    msg_count = 0
    req_count = 0
    if (log_dir / "messages.jsonl").exists():
        msg_count = sum(1 for _ in open(log_dir / "messages.jsonl"))
    if (log_dir / "requirements.jsonl").exists():
        req_count = sum(1 for _ in open(log_dir / "requirements.jsonl"))

    return jsonify({
        "os": f"{uname.system} {uname.release}",
        "host": uname.node,
        "uptime": uptime,
        "ollama_models": model_count,
        "messages_logged": msg_count,
        "requirements_logged": req_count,
        "sessions_active": len(session_manager.sessions),
        "bridge_online": False,  # WhatsApp bridge removed
    })


@app.route("/api/chat/new", methods=["POST"])
def api_chat_new():
    data = request.get_json() or {}
    phone = data.get("phone", "web-ui")
    from main import session_manager as main_sessions
    main_sessions.clear_session(phone)
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = data["message"]
    phone = data.get("phone", "web-ui")
    model_override = data.get("model")

    try:
        if model_override:
            response = handle_message(phone, message, model_override=model_override)
        else:
            response = handle_message(phone, message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/models")
def api_models():
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=10
        )
        ollama_models = []
        for line in result.stdout.strip().split("\n")[1:]:
            parts = line.split()
            if parts:
                ollama_models.append(parts[0])
    except Exception as e:
        ollama_models = []

    opencode_models = [
        {"id": "opencode/deepseek-v4-flash-free", "name": "DeepSeek V4 Flash (opencode cloud)"},
    ]

    return jsonify({
        "ollama_models": ollama_models,
        "opencode_models": opencode_models,
    })


@app.route("/api/agents")
def api_agents():
    agents_dir = Path(os.path.expanduser("~/.config/opencode/agents"))
    agents = []
    if agents_dir.exists():
        for f in sorted(agents_dir.glob("*.md")):
            name = f.stem
            desc = ""
            try:
                content = f.read_text()
                for line in content.split("\n"):
                    if line.startswith("description:"):
                        desc = line[len("description:"):].strip().strip('"').strip("'")
                        break
            except Exception:
                pass
            agents.append({"name": name, "description": desc})
    return jsonify({"agents": agents})


def create_github_issue(text: str) -> str:
    try:
        title = text.split("\n")[0][:80]
        result = subprocess.run(
            ["gh", "issue", "create", "--repo", REPO,
             "--title", f"Requirement: {title}",
             "--body", text,
             "--label", "phase:swe1",
             "--label", "persona:architect"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            gh_project_add(url)
            return url
        return f"gh-error: {result.stderr[:200]}"
    except Exception as e:
        return f"error: {e}"


def gh_project_add(issue_url: str):
    try:
        subprocess.run(
            ["gh", "project", "item-add", "1", "--owner", "NinadAGokhale",
             "--url", issue_url],
            capture_output=True, timeout=15,
        )
    except Exception:
        pass


if __name__ == "__main__":
    print("Dashboard starting at http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=True)
