"""
Tests for Phase 9a agent communication interpreter extensions.

Version: 3.0
Author: Generated for aidev
Change rationale: Phase 9a – verify interpreter execution of define agent, tell,
                  hear, open/close chat, and response field access using a mock
                  gateway.

Covers:
  - define agent with mock config
  - tell (simple and block) dispatches to gateway
  - hear stores response in env
  - response field access (payload, status, tokens, model, error)
  - error cases (undeclared agent, no pending response)
  - open/close chat session lifecycle
"""

from __future__ import annotations

import pytest

from cfd.lexer import lex
from cfd.parser import parse
from cfd.interpreter import CfdRuntimeError, execute, set_gateway

from cfe.agent.gateway import Gateway
from cfe.agent.config import AgentConfig
from cfe.agent.message import Message, Response
from cfe.agent.adapters.base import BaseAdapter


class MockAdapter(BaseAdapter):
    """Adapter that returns a canned response without network I/O."""

    def __init__(self, response_text: str = "mock reply", tokens: int = 10):
        self._response_text = response_text
        self._tokens = tokens
        self.last_message: Message | None = None
        self.call_count = 0

    def send(self, message, config, history):
        self.last_message = message
        self.call_count += 1
        return Response(
            payload=self._response_text,
            status="success",
            tokens=self._tokens,
            model=config.model,
            error=None,
        )


class MockErrorAdapter(BaseAdapter):
    """Adapter that always returns an error response."""

    def send(self, message, config, history):
        return Response(
            payload="",
            status="error",
            tokens=0,
            model=config.model,
            error="something went wrong",
        )


def _make_gateway(adapter=None, agents=None):
    gw = Gateway()
    mock = adapter or MockAdapter()
    gw.register_adapter("mock", mock)
    if agents is None:
        agents = {"testbot": {"vendor": "mock", "model": "test-1"}}
    for name, raw in agents.items():
        cfg = AgentConfig(
            name=name,
            vendor=raw.get("vendor", "mock"),
            model=raw.get("model", "test-1"),
        )
        gw.set_agent_config(name, cfg)
    return gw, mock


def _run(src: str, gw=None, adapter=None, agents=None):
    if gw is None:
        gw, mock = _make_gateway(adapter=adapter, agents=agents)
    else:
        mock = None
    set_gateway(gw)
    try:
        tokens = lex(src)
        stmts = parse(tokens)
        env = execute(stmts)
        return env, gw, mock
    finally:
        set_gateway(None)


# ---------------------------------------------------------------------------
# define agent
# ---------------------------------------------------------------------------

class TestDefineAgent:

    def test_define_agent_success(self):
        env, gw, _ = _run("define agent testbot.")
        assert gw.is_declared("testbot")

    def test_define_agent_not_in_config(self):
        with pytest.raises(CfdRuntimeError, match="not defined in the agent"):
            _run("define agent unknown.")

    def test_define_multiple_agents(self):
        agents = {
            "searcher": {"vendor": "mock", "model": "m1"},
            "writer": {"vendor": "mock", "model": "m2"},
        }
        env, gw, _ = _run(
            "define agent searcher. define agent writer.",
            agents=agents,
        )
        assert gw.is_declared("searcher")
        assert gw.is_declared("writer")


# ---------------------------------------------------------------------------
# tell + hear (simple form)
# ---------------------------------------------------------------------------

class TestTellHearSimple:

    def test_tell_hear_basic(self):
        src = """
        define agent testbot.
        tell testbot text, hello world.
        hear from testbot as reply.
        """
        env, gw, mock = _run(src)
        assert mock.call_count == 1
        assert "reply" in env
        assert isinstance(env["reply"], Response)
        assert env["reply"].payload == "mock reply"
        assert env["reply"].status == "success"

    def test_tell_variable(self):
        src = """
        define agent testbot.
        set msg to text, hi there.
        tell testbot msg.
        hear from testbot as reply.
        """
        env, gw, mock = _run(src)
        assert mock.last_message.text == "hi there"

    def test_tell_undeclared_agent(self):
        gw, _ = _make_gateway()
        with pytest.raises(CfdRuntimeError, match="has not been declared"):
            _run("tell testbot text, hi.", gw=gw)

    def test_hear_without_tell(self):
        with pytest.raises(CfdRuntimeError, match="No pending response"):
            _run("define agent testbot. hear from testbot as reply.")


# ---------------------------------------------------------------------------
# tell (block form)
# ---------------------------------------------------------------------------

class TestTellBlock:

    def test_tell_block_payload(self):
        src = """
        define agent testbot.
        tell testbot.
          set intent to text, search.
          set query to text, python docs.
          set limit to 5.
        end.
        hear from testbot as result.
        """
        env, gw, mock = _run(src)
        msg = mock.last_message
        assert msg.payload == {"intent": "search", "query": "python docs", "limit": 5}
        assert msg.text is None

    def test_tell_block_prompt_rendering(self):
        src = """
        define agent testbot.
        tell testbot.
          set intent to text, search.
          set query to text, hello.
        end.
        hear from testbot as result.
        """
        env, gw, mock = _run(src)
        prompt = mock.last_message.to_prompt()
        assert "intent: search" in prompt
        assert "query: hello" in prompt


# ---------------------------------------------------------------------------
# Response field access
# ---------------------------------------------------------------------------

class TestResponseFields:

    def test_payload(self, capsys):
        src = """
        define agent testbot.
        tell testbot text, go.
        hear from testbot as reply.
        say the payload of reply.
        """
        env, _, _ = _run(src)
        out = capsys.readouterr().out.strip()
        assert out == "mock reply"

    def test_status(self, capsys):
        src = """
        define agent testbot.
        tell testbot text, go.
        hear from testbot as reply.
        say the status of reply.
        """
        env, _, _ = _run(src)
        out = capsys.readouterr().out.strip()
        assert out == "success"

    def test_tokens(self, capsys):
        src = """
        define agent testbot.
        tell testbot text, go.
        hear from testbot as reply.
        say the tokens of reply.
        """
        env, _, _ = _run(src)
        out = capsys.readouterr().out.strip()
        assert out == "10"

    def test_model(self, capsys):
        src = """
        define agent testbot.
        tell testbot text, go.
        hear from testbot as reply.
        say the model of reply.
        """
        env, _, _ = _run(src)
        out = capsys.readouterr().out.strip()
        assert out == "test-1"

    def test_error_on_success(self, capsys):
        src = """
        define agent testbot.
        tell testbot text, go.
        hear from testbot as reply.
        say the error of reply.
        """
        env, _, _ = _run(src)
        out = capsys.readouterr().out.strip()
        assert out == "none"

    def test_error_on_failure(self, capsys):
        src = """
        define agent testbot.
        tell testbot text, go.
        hear from testbot as reply.
        say the error of reply.
        """
        env, _, _ = _run(src, adapter=MockErrorAdapter())
        out = capsys.readouterr().out.strip()
        assert out == "something went wrong"

    def test_field_of_non_response(self):
        with pytest.raises(CfdRuntimeError, match="not an agent response"):
            _run("""
            set x to 5.
            say the payload of x.
            """)

    def test_status_comparison(self, capsys):
        src = """
        define agent testbot.
        tell testbot text, go.
        hear from testbot as reply.
        set ok to text, success.
        if the status of reply is ok then
          say text, ok.
        else
          say text, fail.
        end.
        """
        env, _, _ = _run(src)
        out = capsys.readouterr().out.strip()
        assert out == "ok"


# ---------------------------------------------------------------------------
# open/close chat
# ---------------------------------------------------------------------------

class TestOpenChat:

    def test_chat_session(self, capsys):
        src = """
        define agent testbot.
        open chat session.
          tell testbot text, first.
          hear from testbot as r.
          say the payload of r.
          tell testbot text, second.
          hear from testbot as r.
          say the payload of r.
        close chat.
        """
        env, gw, mock = _run(src)
        assert mock.call_count == 2
        out = capsys.readouterr().out.strip().split("\n")
        assert out == ["mock reply", "mock reply"]

    def test_chat_auto_closes_on_error(self):
        adapter = MockErrorAdapter()
        src = """
        define agent testbot.
        open chat session.
          tell testbot text, fail.
          hear from testbot as r.
        close chat.
        """
        env, gw, _ = _run(src, adapter=adapter)
        assert gw.get_active_session() is None


# ---------------------------------------------------------------------------
# Integration: full agent script
# ---------------------------------------------------------------------------

class TestFullScript:

    def test_multi_agent(self, capsys):
        agents = {
            "searcher": {"vendor": "mock", "model": "search-1"},
            "writer": {"vendor": "mock", "model": "write-1"},
        }
        src = """
        define agent searcher.
        define agent writer.
        open chat tutorial.
          tell searcher.
            set intent to text, search.
            set query to text, python.
          end.
          hear from searcher as found.
          tell writer text, summarize this.
          hear from writer as summary.
          say the payload of summary.
        close chat.
        """
        env, _, _ = _run(src, agents=agents)
        out = capsys.readouterr().out.strip()
        assert out == "mock reply"

    def test_tell_hear_in_loop(self, capsys):
        src = """
        define agent testbot.
        set counter to 0.
        while counter is less than 3 do
          tell testbot text, hello.
          hear from testbot as r.
          set counter to counter plus 1.
        end.
        """
        env, _, mock = _run(src)
        assert mock.call_count == 3
