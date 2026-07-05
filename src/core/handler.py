"""Core message handler for Saratthya — imported by dashboard.py."""

import os
from typing import Optional

from src.core.opencode_wrapper import run_opencode, run_agent, run_ollama, run_opencode_cli
from src.core.command_parser import parse_command, CommandType, AGENT_ALIASES
from src.core.response_formatter import format_response
from src.core.session_manager import SessionManager
from src.core.message_logger import MessageMiddleware, log_requirement
from src.core.content_loader import get_skill_content, get_agent_content

session_manager = SessionManager()


def _build_prompt(agent_name: str, agent_content: str, skill_names: list[str], task: str) -> str:
    """Build a hierarchical prompt: agent as persona, skills as reference, task as request.

    For Ollama mode — both agent and skills are injected as context.
    For opencode cloud mode — the agent_name + skills_context is passed in the task.
    Returns (prompt_string_for_ollama, context_string_for_cloud).
    """
    parts = []
    if agent_name and agent_content:
        agent_body = agent_content[:2500]
        parts.append(f"[Agent: {agent_name}]\n{agent_body}")

    if skill_names:
        skill_blocks = []
        for sn in skill_names:
            sc = get_skill_content(sn)
            if sc:
                skill_blocks.append(f"=== Skill: {sn} ===\n{sc[:1500]}")
        if skill_blocks:
            parts.append("[Active Skills]\n" + "\n\n".join(skill_blocks))

    parts.append(f"[User Request]\n{task}")
    return "\n\n".join(parts)


def _resolve_model(phone: str, text: str, model_override: Optional[str] = None) -> tuple[str, str]:
    """Resolve the model and cleaned text, considering session state."""
    session = session_manager.get_or_create(phone)
    cmd_type, cleaned_text, model = parse_command(text)

    if model_override is not None:
        model = model_override
        session_manager.set_model(phone, model)
        session.current_model = model
    elif model is not None:
        session_manager.set_model(phone, model)
        session.current_model = model
    else:
        model = session.current_model

    return cmd_type, cleaned_text, model


def _handle_message(phone: str, text: str, model_override: Optional[str] = None) -> str:
    """Process an incoming WhatsApp message (internal, no logging)."""
    session = session_manager.get_or_create(phone)
    session.last_command = text

    # Merge session skills with inline skills
    session_skills = list(session.current_skills)

    cmd_type, cleaned_text, model = _resolve_model(phone, text, model_override)

    if cmd_type == CommandType.STATUS:
        return get_status()

    if cmd_type == CommandType.SHELL:
        return execute_shell(cleaned_text)

    if cmd_type == CommandType.FILE:
        return execute_file_op(cleaned_text)

    if cmd_type == CommandType.SEARCH:
        return execute_search(cleaned_text)

    if cmd_type == CommandType.AGENT:
        return execute_agent(cleaned_text, model, extra_skills=session_skills)

    if cmd_type == CommandType.SKILL:
        import re as _re
        # skill: name: agent: subname: task — use agent with skill context
        _m = _re.match(r'^(\S+?):\s*agent:\s*(\S+?):\s*(.*)', cleaned_text, _re.DOTALL)
        if _m:
            _skill_name, _agent_alias, _task = _m.groups()
            # Merge inline skill + session skills
            all_skills = list(session_skills)
            if _skill_name not in all_skills:
                all_skills.append(_skill_name)
            return execute_agent(f"{_agent_alias}: {_task}", model, extra_skills=all_skills)
        # skill: name: task — use skill as context for plain opencode call
        _m = _re.match(r'^(\S+?):\s*(.*)', cleaned_text, _re.DOTALL)
        if _m:
            _skill_name = _m.group(1)
            _task = _m.group(2)
            all_skills = list(session_skills)
            if _skill_name not in all_skills:
                all_skills.append(_skill_name)
            # If no session agent, just run opencode with skills as context
            if session.current_agent:
                return execute_agent(f"{session.current_agent}: {_task}", model, extra_skills=all_skills)
            agent_content = get_skill_content(_skill_name)
            if agent_content:
                _prompt = _build_prompt("", "", all_skills, _task)
            else:
                _prompt = _task
            return run_opencode(_prompt, model=model)

    result = run_opencode(cleaned_text, model=model)
    formatted = format_response(result, full=phone == "web-ui")

    return formatted


handle_message = MessageMiddleware(_handle_message)


def get_status() -> str:
    import platform
    import subprocess
    uname = platform.uname()
    uptime = "N/A"
    try:
        uptime = subprocess.check_output(["uptime"]).decode().strip()
    except Exception:
        pass
    return (
        f"Local AI System\n"
        f"OS: {uname.system} {uname.release}\n"
        f"Node: {uname.node}\n"
        f"Uptime: {uptime}\n"
        f"Sessions: {len(session_manager.sessions)}"
    )


def execute_shell(command: str) -> str:
    import subprocess
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout or result.stderr
        return output[:4000] if output else "Command completed (no output)"
    except subprocess.TimeoutExpired:
        return "Shell command timed out"
    except Exception as e:
        return f"Shell error: {e}"


def execute_file_op(command: str) -> str:
    parts = command.strip().split(maxsplit=1)
    if not parts:
        return "Usage: file: <read|write|edit> <path> [content]"
    action = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""
    if action == "read":
        import glob as glob_mod
        paths = glob_mod.glob(rest)
        if not paths:
            return f"No files matching: {rest}"
        results = []
        for p in paths[:5]:
            try:
                with open(os.path.expanduser(p)) as f:
                    content = f.read()
                results.append(f"--- {p} ---\n{content[:1000]}")
            except Exception as e:
                results.append(f"--- {p} ---\nError: {e}")
        return "\n\n".join(results)
    return "File operations: read <path>"


def execute_agent(command: str, model: str, extra_skills: Optional[list[str]] = None) -> str:
    """Handle agent: prefix — routes to opencode agent with tool execution.
    extra_skills: additional skill names to inject as context alongside the agent.
    """
    parts = command.strip().split(maxsplit=1)
    if not parts:
        agents = ", ".join(sorted(AGENT_ALIASES.keys()))
        return f"Usage: agent: <name> <task>\nAvailable: {agents}\nFull list: cto, growth, founder, engineer, frontend, backend, fullstack, product, project, qa, devops"
    agent_name = parts[0].lower().rstrip(":")
    task = parts[1] if len(parts) > 1 else ""

    agent_name = AGENT_ALIASES.get(agent_name, agent_name)

    if not task:
        return f"Agent '{agent_name}' selected. Send your task after the agent name.\nExample: agent: {agent_name}: build a todo app"

    agent_content = get_agent_content(agent_name)
    skills_list = extra_skills or []

    if model and model.startswith("ollama/"):
        prompt = _build_prompt(agent_name, agent_content, skills_list, task)
        result = run_ollama(prompt, model)
    else:
        # Build context that includes agent description + skills
        context = _build_prompt(agent_name, agent_content, skills_list, task)
        result = run_agent(agent_name, context)
        # If --agent fails (server error), fallback runs --model without agent context
        # Detect and retry with context injected into the fallback
        if _is_agent_fallback_needed(result):
            result = run_opencode_cli(context, model)

    return format_response(result)


def _is_agent_fallback_needed(result: str) -> bool:
    """Check if result indicates opencode --agent failed and fell back to --model."""
    # run_agent returns run_opencode_cli fallback which starts with "As agent"
    # Check for the weak fallback pattern
    return result.startswith("As agent") if result else False


def execute_search(command: str) -> str:
    import subprocess
    try:
        result = subprocess.run(
            ["mdfind", "-name", command],
            capture_output=True, text=True, timeout=15
        )
        lines = result.stdout.strip().split("\n")[:10]
        if not lines or lines == [""]:
            return f"No results for: {command}"
        return "Results:\n" + "\n".join(lines)
    except Exception as e:
        return f"Search error: {e}"
