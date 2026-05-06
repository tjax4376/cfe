"""
CFE Agent Base Adapter – abstract interface for vendor adapters.

Version: 3.0
Author: Generated for aidev
Change rationale: Phase 9a – define the contract that all vendor adapters must
                  implement: send a message with session context, return a
                  Response.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple

from ..config import AgentConfig
from ..message import Message, Response


class BaseAdapter(ABC):
    """Abstract base class for vendor-specific agent adapters."""

    @abstractmethod
    def send(
        self,
        message: Message,
        config: AgentConfig,
        history: List[Tuple[str, str]],
    ) -> Response:
        """Send a message to the agent and return its response.

        Parameters
        ----------
        message : Message
            The outbound message (text or structured payload).
        config : AgentConfig
            The agent's vendor/model configuration.
        history : list of (role, content) tuples
            Conversation history for multi-turn context.

        Returns
        -------
        Response
            The agent's reply with payload, status, token count, etc.
        """

    def supports_streaming(self) -> bool:
        """Whether this adapter supports streaming responses."""
        return False

    def validate_config(self, config: AgentConfig) -> bool:
        """Check that the agent config has all fields this adapter needs."""
        return bool(config.vendor)
