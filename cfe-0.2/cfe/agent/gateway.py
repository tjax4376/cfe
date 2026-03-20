"""
CFE Agent Gateway – routes messages between CFE scripts and AI vendors.

Version: 3.0
Author: Generated for aidev
Change rationale: Phase 9a – core gateway with agent registry, adapter dispatch,
                  session-aware message routing, and depth limiting.

Security:
  - Maximum message depth enforced to prevent infinite agent loops.
  - All network I/O delegated to adapters; gateway itself is transport-agnostic.
  - Agent names must be declared and match config entries.

Design:
  - The gateway is instantiated once per interpreter run.
  - It owns the session manager and adapter registry.
  - The interpreter calls gateway.send() and receives a Response.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .config import AgentConfig, ConfigError, load_config, load_config_from_dict
from .message import Message, Response
from .session import ChatSession, SessionManager
from .adapters.base import BaseAdapter
from .adapters.openai_adapter import OpenAIAdapter
from .adapters.anthropic_adapter import AnthropicAdapter

MAX_MESSAGE_DEPTH = 50


class GatewayError(Exception):
    """Raised for gateway-level failures (config, routing, limits)."""


class Gateway:
    """Central hub for agent communication from CFE scripts."""

    def __init__(self) -> None:
        self._agents: Dict[str, AgentConfig] = {}
        self._declared: Dict[str, bool] = {}
        self._adapters: Dict[str, BaseAdapter] = {}
        self._sessions = SessionManager()
        self._message_depth = 0
        self._config_loaded = False

        self._register_builtin_adapters()

    def _register_builtin_adapters(self) -> None:
        self._adapters["openai"] = OpenAIAdapter()
        self._adapters["anthropic"] = AnthropicAdapter()

    def register_adapter(self, vendor: str, adapter: BaseAdapter) -> None:
        self._adapters[vendor] = adapter

    # -- Configuration -------------------------------------------------------

    def load_agents(self, config_path: Optional[str] = None) -> None:
        """Load agent configs from YAML file."""
        try:
            self._agents = load_config(config_path)
            self._config_loaded = True
        except ConfigError:
            raise

    def load_agents_from_dict(self, data: Dict[str, Any]) -> None:
        """Load agent configs from an in-memory dict (for testing)."""
        self._agents = load_config_from_dict(data)
        self._config_loaded = True

    def set_agent_config(self, name: str, config: AgentConfig) -> None:
        """Directly register an agent config (for testing)."""
        self._agents[name] = config
        self._config_loaded = True

    # -- Agent declaration ---------------------------------------------------

    def declare_agent(self, name: str) -> None:
        """Called by ``define agent <name>.`` in the interpreter."""
        if name not in self._agents:
            raise GatewayError(
                f"Agent '{name}' is not defined in the agent configuration. "
                f"Available agents: {', '.join(sorted(self._agents)) or '(none)'}"
            )
        config = self._agents[name]
        adapter = self._adapters.get(config.vendor)
        if adapter is None:
            raise GatewayError(
                f"No adapter registered for vendor '{config.vendor}' "
                f"(agent '{name}')"
            )
        self._declared[name] = True

    def is_declared(self, name: str) -> bool:
        return name in self._declared

    # -- Session management --------------------------------------------------

    def open_chat(self, name: str) -> ChatSession:
        return self._sessions.open_session(name)

    def close_chat(self, name: str) -> None:
        self._sessions.close_session(name)

    def get_active_session(self) -> Optional[ChatSession]:
        return self._sessions.get_active_session()

    # -- Message sending -----------------------------------------------------

    def send(self, message: Message) -> Response:
        """Send a message to an agent and return the response.

        The gateway:
        1. Validates the agent is declared.
        2. Resolves the adapter for the agent's vendor.
        3. Collects session history if inside a chat block.
        4. Dispatches to the adapter.
        5. Records the exchange in session history.
        """
        agent_name = message.agent_name
        if not self.is_declared(agent_name):
            return Response(
                status="error",
                error=f"Agent '{agent_name}' has not been declared with 'define agent'",
            )

        self._message_depth += 1
        if self._message_depth > MAX_MESSAGE_DEPTH:
            self._message_depth -= 1
            return Response(
                status="error",
                error=f"Maximum message depth ({MAX_MESSAGE_DEPTH}) exceeded",
            )

        try:
            config = self._agents[agent_name]
            adapter = self._adapters[config.vendor]

            history: List[Tuple[str, str]] = []
            session = self._sessions.get_active_session()
            if session is not None:
                history = session.get_history_for_agent(agent_name)

            prompt_text = message.to_prompt()
            if session is not None:
                session.add_turn("user", prompt_text, agent=agent_name)

            response = adapter.send(message, config, history)

            if session is not None and response.status == "success":
                session.add_turn(
                    "assistant", response.payload, agent=agent_name,
                )

            return response
        finally:
            self._message_depth -= 1

    # -- Reset ---------------------------------------------------------------

    def reset(self) -> None:
        """Reset all runtime state (agents stay configured)."""
        self._declared.clear()
        self._sessions.reset()
        self._message_depth = 0
