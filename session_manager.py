import json
import os
import time
import uuid
from typing import Optional

SESSION_FILE = os.path.join(os.path.dirname(__file__), '.sessions.json')
DEFAULT_MODEL = "ollama/qwen2.5-coder:7b"


class Session:
    def __init__(self, phone: str):
        self.phone = phone
        self.history: list[dict] = []
        self.conversations: list[dict] = []
        self.current_model: str = DEFAULT_MODEL
        self.current_agent: Optional[str] = None
        self.current_skill: Optional[str] = None
        self.last_command: Optional[str] = None
        self.context_files: list[str] = []

    def to_dict(self) -> dict:
        return {
            "phone": self.phone,
            "history": self.history[-50:],
            "conversations": self.conversations[-50:],
            "current_model": self.current_model,
            "current_agent": self.current_agent,
            "current_skill": self.current_skill,
            "last_command": self.last_command,
            "context_files": self.context_files,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        s = cls(data["phone"])
        s.history = data.get("history", [])
        s.conversations = data.get("conversations", [])
        s.current_model = data.get("current_model", DEFAULT_MODEL)
        s.current_agent = data.get("current_agent")
        s.current_skill = data.get("current_skill")
        s.last_command = data.get("last_command")
        s.context_files = data.get("context_files", [])
        return s

    def get_title(self) -> str:
        if self.history:
            first = self.history[0].get("content", "")
            return first[:60] if len(first) > 60 else first
        return "New Chat"

    def new_conversation(self) -> str:
        if self.history:
            self.conversations.append({
                "id": str(uuid.uuid4())[:8],
                "title": self.get_title(),
                "history": list(self.history),
            })
        self.history = []
        return ""


class SessionManager:
    def __init__(self):
        self.sessions: dict[str, Session] = {}
        self._load()

    def get_or_create(self, phone: str) -> Session:
        if phone not in self.sessions:
            self.sessions[phone] = Session(phone)
        return self.sessions[phone]

    def add_to_history(self, phone: str, role: str, content: str, latency_ms: Optional[float] = None):
        session = self.get_or_create(phone)
        entry = {"role": role, "content": content, "timestamp": time.time()}
        if latency_ms is not None:
            entry["latency_ms"] = latency_ms
        session.history.append(entry)
        self._save()

    def clear_session(self, phone: str):
        self.sessions.pop(phone, None)
        self._save()

    def new_conversation(self, phone: str):
        session = self.get_or_create(phone)
        session.new_conversation()
        self._save()

    def get_conversations(self, phone: str) -> list[dict]:
        session = self.get_or_create(phone)
        convs = list(session.conversations)
        if session.history:
            convs.insert(0, {
                "id": "__current__",
                "title": session.get_title(),
                "active": True,
            })
        return convs

    def switch_conversation(self, phone: str, conv_id: str) -> list[dict]:
        session = self.get_or_create(phone)
        if conv_id == "__current__":
            return list(session.history)
        for c in session.conversations:
            if c["id"] == conv_id:
                if session.history:
                    session.conversations.append({
                        "id": str(uuid.uuid4())[:8],
                        "title": session.get_title(),
                        "history": list(session.history),
                    })
                session.history = list(c["history"])
                session.conversations = [x for x in session.conversations if x["id"] != conv_id]
                self._save()
                return list(session.history)
        return list(session.history)

    def set_model(self, phone: str, model: str):
        session = self.get_or_create(phone)
        session.current_model = model
        self._save()

    def set_agent(self, phone: str, agent: Optional[str]):
        session = self.get_or_create(phone)
        session.current_agent = agent
        self._save()

    def set_skill(self, phone: str, skill: Optional[str]):
        session = self.get_or_create(phone)
        session.current_skill = skill
        self._save()

    def get_current_agent(self, phone: str) -> Optional[str]:
        return self.get_or_create(phone).current_agent

    def get_current_skill(self, phone: str) -> Optional[str]:
        return self.get_or_create(phone).current_skill

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
