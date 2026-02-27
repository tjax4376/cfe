"""
CFE Agent Session Manager – chat session lifecycle and history.

Version: 3.0
Author: Generated for aidev
Change rationale: Phase 9a – maintain per-chat conversation history so agents
                  can reference prior turns within an ``open chat`` block.

Design:
  - Each session stores an ordered list of (role, content) turns.
  - Sessions are identified by name and created/closed by the interpreter.
  - The session manager enforces a maximum turn limit to prevent runaway
    conversations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


MAX_SESSION_TURNS = 200


class SessionError(Exception):
    """Raised for session lifecycle violations."""


@dataclass
class Turn:
    """A single turn in a conversation."""
    role: str
    content: str
    agent: str = ""


@dataclass
class ChatSession:
    """Holds conversation state for one ``open chat`` block."""

    name: str
    turns: List[Turn] = field(default_factory=list)
    closed: bool = False

    def add_turn(self, role: str, content: str, agent: str = "") -> None:
        if self.closed:
            raise SessionError(
                f"Cannot add turn to closed session '{self.name}'"
            )
        if len(self.turns) >= MAX_SESSION_TURNS:
            raise SessionError(
                f"Session '{self.name}' exceeded maximum turns "
                f"({MAX_SESSION_TURNS})"
            )
        self.turns.append(Turn(role=role, content=content, agent=agent))

    def get_history_for_agent(self, agent_name: str) -> List[Tuple[str, str]]:
        """Return (role, content) pairs relevant to a specific agent.

        Includes all turns where the agent was the target or the responder,
        plus any system-level context.
        """
        history: List[Tuple[str, str]] = []
        for turn in self.turns:
            if turn.agent == agent_name or turn.agent == "":
                history.append((turn.role, turn.content))
        return history

    def close(self) -> None:
        self.closed = True


class SessionManager:
    """Manages the lifecycle of all active chat sessions."""

    def __init__(self) -> None:
        self._sessions: Dict[str, ChatSession] = {}

    def open_session(self, name: str) -> ChatSession:
        if name in self._sessions and not self._sessions[name].closed:
            raise SessionError(
                f"Chat session '{name}' is already open"
            )
        session = ChatSession(name=name)
        self._sessions[name] = session
        return session

    def get_session(self, name: str) -> Optional[ChatSession]:
        session = self._sessions.get(name)
        if session is not None and not session.closed:
            return session
        return None

    def get_active_session(self) -> Optional[ChatSession]:
        """Return the most recently opened non-closed session, if any."""
        for session in reversed(list(self._sessions.values())):
            if not session.closed:
                return session
        return None

    def close_session(self, name: str) -> None:
        session = self._sessions.get(name)
        if session is None:
            raise SessionError(f"No chat session named '{name}' to close")
        session.close()

    def reset(self) -> None:
        """Close all sessions and clear state."""
        self._sessions.clear()
