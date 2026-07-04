import json
import os
from typing import Optional

SESSION_FILE = os.path.join(os.path.dirname(__file__), '.sessions.json')
DEFAULT_MODEL = "ollama/qwen2.5-coder:7b"


class Session:
    def __init__(self, phone: str):
        self.phone = phone
        self.history: list[dict] = []
        self.current_model: str = DEFAULT_MODEL
        self.last_command: Optional[str] = None
        self.context_files: list[str] = []

    def to_dict(self) -> dict:
        return {
            "phone": self.phone,
            "history": self.history[-20:],
            "current_model": self.current_model,
            "last_command": self.last_command,
            "context_files": self.context_files,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        s = cls(data["phone"])
        s.history = data.get("history", [])
        s.current_model = data.get("current_model", DEFAULT_MODEL)
        s.last_command = data.get("last_command")
        s.context_files = data.get("context_files", [])
        return s


class SessionManager:
    def __init__(self):
        self.sessions: dict[str, Session] = {}
        self._load()

    def get_or_create(self, phone: str) -> Session:
        if phone not in self.sessions:
            self.sessions[phone] = Session(phone)
        return self.sessions[phone]

    def add_to_history(self, phone: str, role: str, content: str):
        session = self.get_or_create(phone)
        session.history.append({"role": role, "content": content, "timestamp": __import__('time').time()})
        self._save()

    def set_model(self, phone: str, model: str):
        session = self.get_or_create(phone)
        session.current_model = model
        self._save()

    def _load(self):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE) as f:
                    data = json.load(f)
                    for phone, sdata in data.items():
                        self.sessions[phone] = Session.from_dict(sdata)
            except (json.JSONDecodeError, IOError):
                pass

    def _save(self):
        data = {p: s.to_dict() for p, s in self.sessions.items()}
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f, indent=2)
