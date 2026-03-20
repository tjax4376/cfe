"""
CFE Agent Message Types – data structures for agent communication.

Version: 3.0
Author: Generated for aidev
Change rationale: Phase 9a – Message and Response types used by the gateway,
                  adapters, and interpreter to represent agent I/O.

Metadata:
  - Messages carry a flat key-value payload (or plain text).
  - Responses wrap the agent's reply with status, token count, and model info.
  - Both types are plain dataclasses with no vendor-specific details.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Message:
    """Outbound message sent to an agent via ``tell``."""

    agent_name: str
    chat_name: Optional[str] = None
    text: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

    def to_prompt(self) -> str:
        """Render the message as a single prompt string for the vendor API."""
        if self.text is not None:
            return self.text
        if self.payload:
            parts = [f"{k}: {v}" for k, v in self.payload.items()]
            return "\n".join(parts)
        return ""


@dataclass
class Response:
    """Inbound response received from an agent via ``hear``."""

    payload: str = ""
    status: str = "success"
    tokens: int = 0
    model: str = ""
    error: Optional[str] = None

    _FIELDS = frozenset({"payload", "status", "tokens", "model", "error"})

    def get_field(self, name: str) -> Any:
        """Return a named field value for ``the <field> of <response>``."""
        if name == "payload":
            return self.payload
        if name == "status":
            return self.status
        if name == "tokens":
            return self.tokens
        if name == "model":
            return self.model
        if name == "error":
            return self.error
        raise KeyError(f"Unknown response field: {name!r}")
