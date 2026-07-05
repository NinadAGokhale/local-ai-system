"""Load agent .md and skill SKILL.md file content from disk."""

import os
from pathlib import Path
from typing import Optional


SKILLS_DIR = Path(os.path.expanduser("~/.config/opencode/skills"))
AGENTS_DIR = Path(os.path.expanduser("~/.config/opencode/agents"))
PERSONAS_DIR = Path(os.path.expanduser("~/.config/opencode/personas"))


def get_persona_content(name: str) -> str:
    """Read persona .md content, return empty string if not found."""
    persona_file = PERSONAS_DIR / f"{name}.md"
    if persona_file.exists():
        try:
            return _strip_frontmatter(persona_file.read_text())
        except Exception:
            return ""
    return ""


def get_skill_content(name: str) -> str:
    """Read SKILL.md content for a skill, return empty string if not found."""
    skill_dir = SKILLS_DIR / name
    skill_file = skill_dir / "SKILL.md"
    if skill_file.exists():
        try:
            return _strip_frontmatter(skill_file.read_text())
        except Exception:
            return ""
    # Some skills might be single .md files in skills/
    skill_file = SKILLS_DIR / f"{name}.md"
    if skill_file.exists():
        try:
            return _strip_frontmatter(skill_file.read_text())
        except Exception:
            return ""
    return ""


def get_agent_content(name: str) -> str:
    """Read agent .md content, return empty string if not found."""
    agent_file = AGENTS_DIR / f"{name}.md"
    if agent_file.exists():
        try:
            return _strip_frontmatter(agent_file.read_text())
        except Exception:
            return ""
    return ""


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (--- ... ---) from markdown content."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].strip()
    return text.strip()
