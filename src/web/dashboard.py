"""Saratthya dashboard — Agentic Market Analytics & Business Development."""

import json
import os
import subprocess
from functools import wraps
from pathlib import Path

from flask import Flask, make_response, render_template, request, jsonify, session, redirect, url_for, Response

from src.core.config import PROJECT_ROOT
from src.core.message_logger import get_recent_messages, get_recent_requirements, log_requirement
from src.core.command_parser import parse_command, CommandType, AGENT_ALIASES
from src.core.session_manager import SessionManager
from src.core.handler import handle_message
from src.core.content_loader import get_skill_content, get_agent_content
import traceback

_DOT_ENV = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(_DOT_ENV):
    for _line in open(_DOT_ENV):
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

session_manager = SessionManager()

app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static'))


@app.errorhandler(Exception)
def _handle_exception(e):
    """Catch-all: return JSON instead of HTML for API errors."""
    if request.path.startswith("/api/"):
        tb = traceback.format_exc()
        return jsonify({"error": str(e), "traceback": tb}), 500
    raise e
_SECRET_KEY_FILE = os.path.join(os.path.dirname(__file__), '.secret_key')
if os.path.exists(_SECRET_KEY_FILE):
    app.secret_key = open(_SECRET_KEY_FILE).read().strip()
else:
    app.secret_key = os.urandom(24).hex()
    with open(_SECRET_KEY_FILE, 'w') as f:
        f.write(app.secret_key)

REPO = os.environ.get("SARATTHYA_REPO", "NinadAGokhale/local-ai-system")
GH_PROJECT = os.environ.get("SARATTHYA_GH_PROJECT", "1")
GH_OWNER = os.environ.get("SARATTHYA_GH_OWNER", "NinadAGokhale")

_USERS_ENV = {
    "saee":    "SAEE_PASSWORD",
    "ninad":   "NINAD_PASSWORD",
    "shounak": "SHOUNAK_PASSWORD",
    "sohum":   "SOHUM_PASSWORD",
}
USERS = {}
for _u, _ev in _USERS_ENV.items():
    _pw = os.environ.get(f"SARATTHYA_{_ev}")
    if _pw:
        USERS[_u] = _pw


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def _web_phone():
    return session.get("username", "web-ui")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json() or request.form
        username = data.get("username", "").strip().lower()
        password = data.get("password", "")
        expected = USERS.get(username)
        if expected is not None and password == expected:
            session["logged_in"] = True
            session["username"] = username
            if request.is_json:
                return jsonify({"ok": True, "username": username})
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
    phone = _web_phone()
    s = session_manager.get_or_create(phone)
    conversations = session_manager.get_conversations(phone)
    resp = make_response(render_template(
        "dashboard.html",
        conversations=conversations,
        current_history=s.history,
        current_agent=s.current_agent,
        current_skills=s.current_skills,
        username=session.get("username", "user"),
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

    phone = data.get("phone") or _web_phone()
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
    phone = request.args.get("phone") or _web_phone()
    convs = session_manager.get_conversations(phone)
    return jsonify(convs)


@app.route("/api/conversations", methods=["POST"])
def api_switch_conversation():
    data = request.get_json() or {}
    phone = data.get("phone") or _web_phone()
    conv_id = data.get("conv_id")
    if not conv_id:
        return jsonify({"error": "Missing conv_id"}), 400
    history = session_manager.switch_conversation(phone, conv_id)
    s = session_manager.get_or_create(phone)
    return jsonify({
        "history": history,
        "current_agent": s.current_agent,
        "current_skills": s.current_skills,
    })


@app.route("/api/chat/new", methods=["POST"])
def api_chat_new():
    data = request.get_json() or {}
    phone = data.get("phone") or _web_phone()
    session_manager.new_conversation(phone)
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    import time
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = data["message"]
    phone = data.get("phone") or _web_phone()
    model_override = data.get("model")

    s = session_manager.get_or_create(phone)

    # Prefix message so parse_command detects agent/skill mode.
    # Handler reads session.current_skills and session.current_agent directly.
    if s.current_agent:
        message = f"agent: {s.current_agent}: {message}"
    elif s.current_skills:
        message = f"skill: {s.current_skills[0]}: {message}"

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


@app.route("/api/me")
@login_required
def api_me():
    return jsonify({"username": session.get("username", "unknown")})


@app.route("/api/chat/download", methods=["GET"])
def api_chat_download():
    phone = request.args.get("phone") or _web_phone()
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
    phone = data.get("phone") or _web_phone()
    agent = data.get("agent") or None
    session_manager.set_agent(phone, agent)
    return jsonify({"ok": True, "current_agent": agent})


@app.route("/api/skill", methods=["POST"])
def api_set_skill():
    """Toggle a skill on/off. POST with skill='name' adds it; without removes all."""
    data = request.get_json() or {}
    phone = data.get("phone") or _web_phone()
    skill = data.get("skill")
    if skill:
        session_manager.toggle_skill(phone, skill)
    else:
        session_manager.clear_skills(phone)
    return jsonify({"ok": True, "current_skills": session_manager.get_current_skills(phone)})


EMOJI_CATEGORY = {
    "🧠": "reasoning",
    "📝": "coding",
    "🌐": "general",
    "⚡": "quick",
}

def _model_category(emoji, desc):
    """Derive task category from emoji or desc. Falls back to 'general'."""
    if emoji in EMOJI_CATEGORY:
        return EMOJI_CATEGORY[emoji]
    for e, cat in EMOJI_CATEGORY.items():
        if e in desc:
            return cat
    return "general"

@app.route("/api/models")
def api_models():
    ollama_models = []
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=10
        )
        from src.core.mlx_wrapper import get_model_meta
        for line in result.stdout.strip().split("\n")[1:]:
            parts = line.split()
            if parts:
                name = parts[0]
                meta = get_model_meta(f"ollama/{name}")
                ollama_models.append({
                    "id": f"ollama/{name}",
                    "name": meta["label"],
                    "emoji": meta["emoji"],
                    "desc": meta["desc"],
                    "category": _model_category(meta["emoji"], meta["desc"]),
                })
        ollama_up = True
    except Exception:
        ollama_up = False

    OPENCODE_GO_MODELS = {
        "opencode-go/deepseek-v4-flash": {"emoji": "☁️", "label": "DeepSeek V4 Flash", "desc": "⚡ Fast – 2-8 sec. Best value cloud model."},
        "opencode-go/deepseek-v4-pro": {"emoji": "☁️", "label": "DeepSeek V4 Pro", "desc": "🧠 Thinking – 10-40 sec. DeepSeek's most powerful."},
        "opencode-go/glm-5.1": {"emoji": "☁️", "label": "GLM 5.1", "desc": "🌐 General – 3-10 sec. ZhipuAI capable chat model."},
        "opencode-go/glm-5.2": {"emoji": "☁️", "label": "GLM 5.2", "desc": "🌐 General – 3-10 sec. ZhipuAI latest."},
        "opencode-go/kimi-k2.6": {"emoji": "☁️", "label": "Kimi K2.6", "desc": "🌐 General – 3-10 sec. Moonshot assistant."},
        "opencode-go/kimi-k2.7-code": {"emoji": "☁️", "label": "Kimi K2.7 Code", "desc": "📝 Coding – 5-15 sec. Moonshot coding specialist."},
        "opencode-go/mimo-v2.5": {"emoji": "☁️", "label": "MiMo V2.5", "desc": "⚡ Fast – 1-4 sec. Lightweight cloud model."},
        "opencode-go/mimo-v2.5-pro": {"emoji": "☁️", "label": "MiMo V2.5 Pro", "desc": "🌐 General – 3-10 sec. Capable cloud model."},
        "opencode-go/minimax-m2.7": {"emoji": "☁️", "label": "MiniMax M2.7", "desc": "🌐 General – 3-10 sec. MiniMax assistant."},
        "opencode-go/minimax-m3": {"emoji": "☁️", "label": "MiniMax M3", "desc": "🧠 Thinking – 10-30 sec. MiniMax's best reasoning model."},
        "opencode-go/qwen3.6-plus": {"emoji": "☁️", "label": "Qwen 3.6 Plus", "desc": "🌐 General – 3-10 sec. Alibaba's strong all-rounder."},
        "opencode-go/qwen3.7-max": {"emoji": "☁️", "label": "Qwen 3.7 Max", "desc": "🧠 Thinking – 10-30 sec. Alibaba's most powerful model."},
        "opencode-go/qwen3.7-plus": {"emoji": "☁️", "label": "Qwen 3.7 Plus", "desc": "🌐 General – 3-10 sec. Alibaba's balanced model."},
    }
    opencode_models = [
        {"id": mid, "name": meta["label"], "emoji": meta["emoji"],
         "desc": meta["desc"], "category": _model_category(meta["emoji"], meta["desc"])}
        for mid, meta in OPENCODE_GO_MODELS.items()
    ]

    mlx_models = []
    mlx_up = False
    try:
        from src.core.mlx_wrapper import is_server_running, list_cached_models, get_model_meta
        mlx_up = is_server_running()
        for repo_id in list_cached_models():
            short = repo_id.split("/", 1)[-1]
            mid = f"mlx/{short}"
            meta = get_model_meta(mid)
            mlx_models.append({
                "id": mid,
                "name": meta["label"],
                "emoji": meta["emoji"],
                "desc": meta["desc"],
                "category": _model_category(meta["emoji"], meta["desc"]),
            })
    except Exception:
        pass

    return jsonify({
        "ollama_models": ollama_models,
        "ollama_up": ollama_up,
        "opencode_models": opencode_models,
        "opencode_up": True,
        "mlx_models": mlx_models,
        "mlx_up": mlx_up,
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


@app.route("/api/debug/resolve", methods=["POST"])
def api_debug_resolve():
    """Debug endpoint that shows how a message will be processed without executing.
    Returns the resolved command type, model, extracted skill/agent names, content sizes, etc.
    """
    data = request.get_json() or {}
    message = data.get("message", "")
    phone = data.get("phone") or _web_phone()
    model_override = data.get("model")

    s = session_manager.get_or_create(phone)
    original = message

    if s.current_agent:
        message = f"agent: {s.current_agent}: {message}"
    elif s.current_skills:
        message = f"skill: {s.current_skills[0]}: {message}"

    cmd_type, cleaned_text, resolved_model = parse_command(message)
    if model_override:
        resolved_model = model_override
    elif resolved_model is None:
        resolved_model = s.current_model

    info = {
        "original_message": original,
        "prefixed_message": message if message != original else None,
        "cmd_type": cmd_type.value,
        "cleaned_text": cleaned_text,
        "resolved_model": resolved_model,
        "session_agent": s.current_agent,
        "session_skills": s.current_skills,
        "skill_names": list(s.current_skills),
    }

    if cmd_type.value == "agent":
        parts = cleaned_text.strip().split(maxsplit=1)
        if parts:
            an = parts[0].lower().rstrip(":")
            an = AGENT_ALIASES.get(an, an)
            ac = get_agent_content(an)
            info["agent_name"] = an
            info["agent_content_chars"] = len(ac)
            info["agent_content_excerpt"] = ac[:200] if ac else ""
            if resolved_model and resolved_model.startswith("ollama/"):
                info["_will_call"] = "run_ollama (agent)"
                info["_ollama_agent_has_content"] = bool(ac)
            else:
                info["_will_call"] = "run_agent (opencode CLI)"
            # Show skills that will be injected alongside the agent
            extra_skills = s.current_skills
            skill_sizes = {sk: len(get_skill_content(sk)) for sk in extra_skills}
            info["extra_skills"] = {sk: f"{sz}c" for sk, sz in skill_sizes.items() if sz > 0}

    elif cmd_type.value == "skill":
        import re as _re
        _m = _re.match(r'^(\S+?):\s*(.*)', cleaned_text, _re.DOTALL)
        if _m:
            sk, tk = _m.groups()
            sc = get_skill_content(sk)
            info["skill_name"] = sk
            info["skill_content_chars"] = len(sc)
            info["skill_content_excerpt"] = sc[:200] if sc else ""
            # Show all session skills
            extra_skills = [sk] + [s for s in s.current_skills if s != sk]
            skill_sizes = {sk: len(get_skill_content(sk)) for sk in extra_skills}
            info["extra_skills"] = {sk: f"{sz}c" for sk, sz in skill_sizes.items() if sz > 0}
            if s.current_agent:
                info["_will_call"] = "execute_agent (agent+skills)"
                an = AGENT_ALIASES.get(s.current_agent, s.current_agent)
                ac = get_agent_content(an)
                info["agent_name"] = an
                info["agent_content_chars"] = len(ac)
            elif resolved_model and resolved_model.startswith("ollama/"):
                info["_will_call"] = "run_ollama (skills-only)"
            else:
                info["_will_call"] = "run_opencode (skills-only)"

    return jsonify(info)


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
            ["gh", "project", "item-add", GH_PROJECT, "--owner", GH_OWNER,
             "--url", issue_url],
            capture_output=True, timeout=15,
        )
    except Exception:
        pass
