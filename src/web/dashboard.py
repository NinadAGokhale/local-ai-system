"""Saratthya dashboard — Agentic Market Analytics & Business Development."""

import json
import os
import subprocess
from functools import wraps
from pathlib import Path

from flask import Flask, make_response, render_template, request, jsonify, session, redirect, url_for, Response

from src.core.config import PROJECT_ROOT
from src.core.message_logger import get_recent_messages, get_recent_requirements, log_requirement
from src.core.command_parser import parse_command, CommandType
from src.core.session_manager import SessionManager
from src.core.handler import handle_message

session_manager = SessionManager()

app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.secret_key = os.urandom(24).hex()

REPO = "NinadAGokhale/local-ai-system"

LOGIN_USER = "user"
LOGIN_PASS = "password123"


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json() or request.form
        if data.get("username") == LOGIN_USER and data.get("password") == LOGIN_PASS:
            session["logged_in"] = True
            if request.is_json:
                return jsonify({"ok": True})
            return redirect(url_for("index"))
        if request.is_json:
            return jsonify({"ok": False, "error": "Invalid credentials"}), 401
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    phone = "web-ui"
    s = session_manager.get_or_create(phone)
    conversations = session_manager.get_conversations(phone)
    resp = make_response(render_template(
        "dashboard.html",
        conversations=conversations,
        current_history=s.history,
        current_agent=s.current_agent,
        current_skill=s.current_skill,
    ))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


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

    log_dir = Path(PROJECT_ROOT) / "logs"
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
    })


@app.route("/api/conversations", methods=["GET"])
def api_conversations():
    phone = request.args.get("phone", "web-ui")
    convs = session_manager.get_conversations(phone)
    return jsonify(convs)


@app.route("/api/conversations", methods=["POST"])
def api_switch_conversation():
    data = request.get_json() or {}
    phone = data.get("phone", "web-ui")
    conv_id = data.get("conv_id")
    if not conv_id:
        return jsonify({"error": "Missing conv_id"}), 400
    history = session_manager.switch_conversation(phone, conv_id)
    s = session_manager.get_or_create(phone)
    return jsonify({
        "history": history,
        "current_agent": s.current_agent,
        "current_skill": s.current_skill,
    })


@app.route("/api/chat/new", methods=["POST"])
def api_chat_new():
    data = request.get_json() or {}
    phone = data.get("phone", "web-ui")
    session_manager.new_conversation(phone)
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    import time
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = data["message"]
    phone = data.get("phone", "web-ui")
    model_override = data.get("model")

    s = session_manager.get_or_create(phone)

    # Apply active mode prefix — skill takes priority when both active
    if s.current_skill:
        message = f"skill: {s.current_skill}: {message}"
    elif s.current_agent:
        message = f"agent: {s.current_agent}: {message}"

    session_manager.add_to_history(phone, "user", data["message"])

    start = time.time()
    try:
        if model_override:
            response = handle_message(phone, message, model_override=model_override)
        else:
            response = handle_message(phone, message)
        latency_ms = (time.time() - start) * 1000
        session_manager.add_to_history(phone, "bot", response, latency_ms=latency_ms)
        return jsonify({"response": response})
    except Exception as e:
        session_manager.add_to_history(phone, "bot", f"Error: {e}", latency_ms=0)
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat/download", methods=["GET"])
def api_chat_download():
    phone = request.args.get("phone", "web-ui")
    fmt = request.args.get("format", "json")
    s = session_manager.get_or_create(phone)
    if fmt == "txt":
        lines = []
        for msg in s.history:
            role = msg.get("role", "unknown")
            text = msg.get("content", "")
            lines.append(f"[{role.upper()}] {text}\n")
        return Response("\n".join(lines), mimetype="text/plain",
                        headers={"Content-Disposition": "attachment; filename=chat.txt"})
    return jsonify(s.history)


@app.route("/api/agent", methods=["POST"])
def api_set_agent():
    data = request.get_json() or {}
    phone = data.get("phone", "web-ui")
    agent = data.get("agent") or None
    session_manager.set_agent(phone, agent)
    return jsonify({"ok": True, "current_agent": agent})


@app.route("/api/skill", methods=["POST"])
def api_set_skill():
    data = request.get_json() or {}
    phone = data.get("phone", "web-ui")
    skill = data.get("skill") or None
    session_manager.set_skill(phone, skill)
    return jsonify({"ok": True, "current_skill": skill})


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
            if name.lower() in ("readme", "template"):
                continue
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


@app.route("/api/skills")
def api_skills():
    skills_dir = Path(os.path.expanduser("~/.config/opencode/skills"))
    skills = []
    if skills_dir.exists():
        for f in sorted(skills_dir.iterdir()):
            if f.is_dir():
                skill_file = f / "SKILL.md"
                if skill_file.exists():
                    name = f.name
                    desc = ""
                    try:
                        content = skill_file.read_text()
                        for line in content.split("\n"):
                            if line.startswith("description:"):
                                desc = line[len("description:"):].strip().strip('"').strip("'")
                                break
                    except Exception:
                        pass
                    skills.append({"name": name, "description": desc})
            elif f.suffix == ".md" and f.stem.lower() not in ("readme", "template"):
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
                skills.append({"name": name, "description": desc})
    return jsonify({"skills": skills})


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
