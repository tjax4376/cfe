"""
Tests for Phase 9a agent gateway, config, and session management.

Version: 3.0
Author: Generated for aidev
Change rationale: Phase 9a – verify gateway dispatch, adapter registry,
                  config loading/validation, and session lifecycle with mock
                  HTTP.

Covers:
  - AgentConfig parsing and validation
  - ConfigError cases (missing vendor, unsupported vendor, missing env var)
  - load_config_from_dict
  - Gateway agent declaration and dispatch
  - Session lifecycle (open, add turn, close)
  - Message depth limiting
  - Response field access via Response.get_field()
"""

from __future__ import annotations

import os
import pytest
from typing import List, Tuple

from cfe.agent.config import (
    AgentConfig,
    ConfigError,
    load_config_from_dict,
)
from cfe.agent.message import Message, Response
from cfe.agent.session import (
    ChatSession,
    SessionError,
    SessionManager,
    Turn,
)
from cfe.agent.gateway import Gateway, GatewayError
from cfe.agent.adapters.base import BaseAdapter


class EchoAdapter(BaseAdapter):
    """Test adapter that echoes the message prompt back."""

    def send(self, message, config, history):
        return Response(
            payload=f"echo: {message.to_prompt()}",
            status="success",
            tokens=5,
            model=config.model,
        )


class CountingAdapter(BaseAdapter):
    """Test adapter that counts calls."""

    def __init__(self):
        self.calls = 0
        self.history_lengths: List[int] = []

    def send(self, message, config, history):
        self.calls += 1
        self.history_lengths.append(len(history))
        return Response(
            payload=f"call {self.calls}",
            status="success",
            tokens=1,
            model=config.model,
        )


# ---------------------------------------------------------------------------
# AgentConfig + load_config_from_dict
# ---------------------------------------------------------------------------

class TestConfig:

    def test_basic_config(self):
        data = {
            "agents": {
                "bot": {
                    "vendor": "openai",
                    "model": "gpt-4o",
                    "system_prompt": "You are a helper.",
                    "max_tokens": 500,
                    "temperature": 0.5,
                }
            }
        }
        os.environ["TEST_KEY_UNUSED"] = "dummy"
        configs = load_config_from_dict(data)
        assert "bot" in configs
        cfg = configs["bot"]
        assert cfg.vendor == "openai"
        assert cfg.model == "gpt-4o"
        assert cfg.max_tokens == 500
        assert cfg.temperature == 0.5

    def test_missing_vendor(self):
        with pytest.raises(ConfigError, match="missing required field 'vendor'"):
            load_config_from_dict({
                "agents": {"bot": {"model": "x"}}
            })

    def test_unsupported_vendor(self):
        with pytest.raises(ConfigError, match="unsupported vendor"):
            load_config_from_dict({
                "agents": {"bot": {"vendor": "unknown"}}
            })

    def test_env_var_resolution(self):
        os.environ["CFE_TEST_API_KEY"] = "sk-test-123"
        try:
            configs = load_config_from_dict({
                "agents": {
                    "bot": {
                        "vendor": "openai",
                        "model": "gpt-4o",
                        "api_key_env": "CFE_TEST_API_KEY",
                    }
                }
            })
            assert configs["bot"].api_key == "sk-test-123"
        finally:
            del os.environ["CFE_TEST_API_KEY"]

    def test_missing_env_var(self):
        env_name = "CFE_NONEXISTENT_KEY_12345"
        if env_name in os.environ:
            del os.environ[env_name]
        with pytest.raises(ConfigError, match="not set or empty"):
            load_config_from_dict({
                "agents": {
                    "bot": {
                        "vendor": "openai",
                        "api_key_env": env_name,
                    }
                }
            })


# ---------------------------------------------------------------------------
# Session lifecycle
# ---------------------------------------------------------------------------

class TestSessionManager:

    def test_open_close(self):
        mgr = SessionManager()
        session = mgr.open_session("test")
        assert isinstance(session, ChatSession)
        assert session.name == "test"
        mgr.close_session("test")
        assert mgr.get_session("test") is None

    def test_duplicate_open(self):
        mgr = SessionManager()
        mgr.open_session("test")
        with pytest.raises(SessionError, match="already open"):
            mgr.open_session("test")

    def test_close_nonexistent(self):
        mgr = SessionManager()
        with pytest.raises(SessionError, match="No chat session"):
            mgr.close_session("ghost")

    def test_add_turn(self):
        mgr = SessionManager()
        session = mgr.open_session("test")
        session.add_turn("user", "hello", agent="bot")
        session.add_turn("assistant", "hi there", agent="bot")
        assert len(session.turns) == 2

    def test_turn_on_closed_session(self):
        mgr = SessionManager()
        session = mgr.open_session("test")
        mgr.close_session("test")
        with pytest.raises(SessionError, match="closed session"):
            session.add_turn("user", "late message")

    def test_history_for_agent(self):
        session = ChatSession(name="test")
        session.add_turn("user", "search", agent="searcher")
        session.add_turn("assistant", "found", agent="searcher")
        session.add_turn("user", "write", agent="writer")
        session.add_turn("assistant", "done", agent="writer")

        history = session.get_history_for_agent("searcher")
        assert len(history) == 2
        assert history[0] == ("user", "search")
        assert history[1] == ("assistant", "found")

    def test_get_active_session(self):
        mgr = SessionManager()
        assert mgr.get_active_session() is None
        mgr.open_session("first")
        assert mgr.get_active_session().name == "first"
        mgr.open_session("second")
        assert mgr.get_active_session().name == "second"
        mgr.close_session("second")
        assert mgr.get_active_session().name == "first"


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class TestResponse:

    def test_get_field_payload(self):
        r = Response(payload="hello", status="success", tokens=5, model="m1")
        assert r.get_field("payload") == "hello"

    def test_get_field_status(self):
        r = Response(status="error")
        assert r.get_field("status") == "error"

    def test_get_field_error(self):
        r = Response(error="bad")
        assert r.get_field("error") == "bad"

    def test_get_field_unknown(self):
        r = Response()
        with pytest.raises(KeyError, match="Unknown"):
            r.get_field("bogus")


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------

class TestMessage:

    def test_text_prompt(self):
        m = Message(agent_name="bot", text="hello")
        assert m.to_prompt() == "hello"

    def test_payload_prompt(self):
        m = Message(agent_name="bot", payload={"intent": "search", "query": "python"})
        prompt = m.to_prompt()
        assert "intent: search" in prompt
        assert "query: python" in prompt

    def test_empty_prompt(self):
        m = Message(agent_name="bot")
        assert m.to_prompt() == ""


# ---------------------------------------------------------------------------
# Gateway
# ---------------------------------------------------------------------------

class TestGateway:

    def _make_gw(self, adapter=None):
        gw = Gateway()
        a = adapter or EchoAdapter()
        gw.register_adapter("mock", a)
        gw.set_agent_config("bot", AgentConfig(
            name="bot", vendor="mock", model="echo-1",
        ))
        return gw, a

    def test_declare_and_send(self):
        gw, _ = self._make_gw()
        gw.declare_agent("bot")
        msg = Message(agent_name="bot", text="ping")
        resp = gw.send(msg)
        assert resp.status == "success"
        assert resp.payload == "echo: ping"

    def test_send_undeclared(self):
        gw, _ = self._make_gw()
        msg = Message(agent_name="bot", text="ping")
        resp = gw.send(msg)
        assert resp.status == "error"
        assert "not been declared" in resp.error

    def test_declare_unknown_agent(self):
        gw, _ = self._make_gw()
        with pytest.raises(GatewayError, match="not defined"):
            gw.declare_agent("ghost")

    def test_session_history(self):
        adapter = CountingAdapter()
        gw, _ = self._make_gw(adapter=adapter)
        gw.declare_agent("bot")

        session = gw.open_chat("test")
        msg1 = Message(agent_name="bot", text="first")
        gw.send(msg1)
        msg2 = Message(agent_name="bot", text="second")
        gw.send(msg2)
        gw.close_chat("test")

        assert adapter.calls == 2
        assert adapter.history_lengths[0] == 0
        assert adapter.history_lengths[1] == 2

    def test_message_depth_limit(self):
        gw, _ = self._make_gw()
        gw.declare_agent("bot")
        gw._message_depth = 50
        msg = Message(agent_name="bot", text="overflow")
        resp = gw.send(msg)
        assert resp.status == "error"
        assert "depth" in resp.error.lower()

    def test_reset(self):
        gw, _ = self._make_gw()
        gw.declare_agent("bot")
        gw.open_chat("test")
        gw.reset()
        assert not gw.is_declared("bot")
        assert gw.get_active_session() is None
