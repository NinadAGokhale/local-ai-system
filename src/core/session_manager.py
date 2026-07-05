import json
import os
import threading
import time
import uuid
from typing import Optional

from src.core.config import SESSION_FILE, DEFAULT_MODEL


class Session:
    def __init__(self, phone: str):
        self.phone = phone
        self.history: list[dict] = []
        self.conversations: list[dict] = []
        self.current_model: str = DEFAULT_MODEL
        self.current_agent: Optional[str] = None
        self.current_skills: list[str] = []
        self.last_command: Optional[str] = None
        self.context_files: list[str] = []
        self.current_conv_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "phone": self.phone,
            "history": self.history[-50:],
            "conversations": self.conversations[-50:],
            "current_model": self.current_model,
            "current_agent": self.current_agent,
            "current_skills": self.current_skills,
            "last_command": self.last_command,
            "context_files": self.context_files,
            "current_conv_id": self.current_conv_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        s = cls(data["phone"])
        s.history = data.get("history", [])
        s.conversations = data.get("conversations", [])
        s.current_model = data.get("current_model", DEFAULT_MODEL)
        s.current_agent = data.get("current_agent")
        s.current_skills = data.get("current_skills", [])
        s.last_command = data.get("last_command")
        s.context_files = data.get("context_files", [])
        s.current_conv_id = data.get("current_conv_id")
        return s

    def get_title(self) -> str:
        if self.history:
            first = self.history[0].get("content", "")
            return first[:60] if len(first) > 60 else first
        return "New Chat"


class SessionManager:
    def __init__(self, session_file: Optional[str] = None):
        self.sessions: dict[str, Session] = {}
        self._lock = threading.Lock()
        self._session_file = session_file or SESSION_FILE
        self._load()

    def get_or_create(self, phone: str) -> Session:
        if phone not in self.sessions:
            self.sessions[phone] = Session(phone)
        return self.sessions[phone]

    def _ensure_conv_id(self, session: Session):
        """Ensure session has a current_conv_id set."""
        if session.current_conv_id is None and session.history:
            session.current_conv_id = "__current__"

    def _save_current_conversation(self, session: Session):
        """Save or update the current conversation's history in-place."""
        if not session.history:
            return
        self._ensure_conv_id(session)
        if session.current_conv_id and session.current_conv_id != "__current__":
            # Update existing saved conversation in-place
            for c in session.conversations:
                if c["id"] == session.current_conv_id:
                    c["title"] = session.get_title()
                    c["history"] = list(session.history)
                    return
        # New unsaved conversation — create a new entry
        session.conversations.append({
            "id": str(uuid.uuid4())[:8],
            "title": session.get_title(),
            "history": list(session.history),
        })

    def add_to_history(self, phone: str, role: str, content: str, latency_ms: Optional[float] = None):
        session = self.get_or_create(phone)
        entry = {"role": role, "content": content, "timestamp": time.time()}
        if latency_ms is not None:
            entry["latency_ms"] = latency_ms
        session.history.append(entry)
        self._ensure_conv_id(session)
        self._save()

    def clear_session(self, phone: str):
        self.sessions.pop(phone, None)
        self._save()

    def new_conversation(self, phone: str):
        """Save current conversation and start a fresh one."""
        session = self.get_or_create(phone)
        if session.history:
            self._save_current_conversation(session)
        session.history = []
        session.current_conv_id = "__current__"
        self._save()

    def get_conversations(self, phone: str) -> list[dict]:
        session = self.get_or_create(phone)
        convs = []
        active_id = session.current_conv_id or "__current__"
        # Add saved conversations, marking the active one
        for c in session.conversations:
            convs.append({
                "id": c["id"],
                "title": c["title"],
                "active": c["id"] == active_id,
            })
        # Add __current__ if there's active history not yet saved
        if session.history and active_id == "__current__":
            convs.insert(0, {
                "id": "__current__",
                "title": session.get_title(),
                "active": True,
            })
        return convs

    def switch_conversation(self, phone: str, conv_id: str) -> list[dict]:
        """Switch to a saved or new conversation.
        Saves current history in-place before switching, then loads the target.
        Both remain in the sidebar — no duplicates."""
        session = self.get_or_create(phone)
        # If already on this conversation, just return
        if session.current_conv_id == conv_id and conv_id != "__current__":
            return list(session.history)
        if conv_id == "__current__":
            return list(session.history)
        # Save current history in-place before switching
        if session.history:
            self._save_current_conversation(session)
            session.history = []
        # Load the target conversation
        for c in session.conversations:
            if c["id"] == conv_id:
                session.history = list(c["history"])
                session.current_conv_id = conv_id
                self._save()
                return list(session.history)
        session.current_conv_id = "__current__"
        self._save()
        return list(session.history)

    def set_model(self, phone: str, model: str):
        session = self.get_or_create(phone)
        session.current_model = model
        self._save()

    def set_agent(self, phone: str, agent: Optional[str]):
        session = self.get_or_create(phone)
        session.current_agent = agent
        self._save()

    def toggle_skill(self, phone: str, skill: str):
        """Add skill to list if not present, remove if already present."""
        session = self.get_or_create(phone)
        if skill in session.current_skills:
            session.current_skills = [s for s in session.current_skills if s != skill]
        else:
            session.current_skills.append(skill)
        self._save()

    def set_skills(self, phone: str, skills: list[str]):
        session = self.get_or_create(phone)
        session.current_skills = skills
        self._save()

    def clear_skills(self, phone: str):
        session = self.get_or_create(phone)
        session.current_skills = []
        self._save()

    def get_current_agent(self, phone: str) -> Optional[str]:
        return self.get_or_create(phone).current_agent

    def get_current_skills(self, phone: str) -> list[str]:
        return list(self.get_or_create(phone).current_skills)

    def _load(self):
        with self._lock:
            if os.path.exists(self._session_file):
                try:
                    with open(self._session_file) as f:
                        data = json.load(f)
                        for phone, sdata in data.items():
                            self.sessions[phone] = Session.from_dict(sdata)
                except (json.JSONDecodeError, IOError):
                    pass

    def _save(self):
        with self._lock:
            data = {p: s.to_dict() for p, s in self.sessions.items()}
            tmp = self._session_file + ".tmp"
            with open(tmp, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, self._session_file)
