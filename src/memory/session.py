from typing import Protocol, Optional
from dataclasses import dataclass, field

@dataclass
class ConversationTurn:
    turn_number: int
    query: str
    agent: str
    response_summary: str

class SessionMemory(Protocol):
    def get_history(self, session_id: str, last_n: int = 5) -> list[dict]:
        """Retrieve the last N turns for a session."""
        ...

    def add_turn(self, session_id: str, turn: dict) -> None:
        """Add a new turn to the session history."""
        ...

    def clear(self, session_id: str) -> None:
        """Clear history for a session."""
        ...

    def get_cache(self, session_id: str, query: str) -> Optional[dict]:
        """Retrieve a cached classifier result for a specific query in a session."""
        ...

    def set_cache(self, session_id: str, query: str, output: dict) -> None:
        """Cache a classifier result for a session."""
        ...

class InMemorySessionMemory:
    """In-memory implementation of SessionMemory."""
    def __init__(self):
        self._storage: dict[str, list[dict]] = {}
        self._cache: dict[str, dict[str, dict]] = {} # session_id -> {query -> output}

    def get_history(self, session_id: str, last_n: int = 5) -> list[dict]:
        history = self._storage.get(session_id, [])
        return history[-last_n:]

    def add_turn(self, session_id: str, turn: dict) -> None:
        if session_id not in self._storage:
            self._storage[session_id] = []
        self._storage[session_id].append(turn)

    def clear(self, session_id: str) -> None:
        if session_id in self._storage:
            del self._storage[session_id]
        if session_id in self._cache:
            del self._cache[session_id]

    def get_cache(self, session_id: str, query: str) -> Optional[dict]:
        session_cache = self._cache.get(session_id, {})
        return session_cache.get(query.lower().strip())

    def set_cache(self, session_id: str, query: str, output: dict) -> None:
        if session_id not in self._cache:
            self._cache[session_id] = {}
        self._cache[session_id][query.lower().strip()] = output


# Singleton instance for easy access
_memory_instance: Optional[SessionMemory] = None

def get_session_memory() -> SessionMemory:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = InMemorySessionMemory()
    return _memory_instance
