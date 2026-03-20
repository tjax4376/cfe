"""
Tests for Phase 9a agent communication parser extensions.

Version: 3.0
Author: Generated for aidev
Change rationale: Phase 9a – verify parsing of define agent, tell, hear,
                  open/close chat, and response field access expressions.

Covers:
  - DefineAgentStmt parsing (valid and invalid)
  - TellStmt (simple form and block form)
  - HearStmt (basic and with timeout)
  - OpenChatStmt (body parsing, unterminated error)
  - ResponseFieldExpr in expressions
  - Interaction with existing syntax (tell inside if/while)
"""

from __future__ import annotations

import pytest

from cfe.lexer import lex
from cfe.parser import (
    DefineAgentStmt,
    HearStmt,
    IfStmt,
    NumberLiteral,
    OpenChatStmt,
    ParseError,
    ResponseFieldExpr,
    SayStmt,
    SetStmt,
    TellStmt,
    TextLiteral,
    VarRef,
    WhileStmt,
    parse,
)


def _parse(src: str):
    return parse(lex(src))


# ---------------------------------------------------------------------------
# define agent
# ---------------------------------------------------------------------------

class TestDefineAgent:

    def test_define_agent_basic(self):
        stmts = _parse("define agent searcher.")
        assert len(stmts) == 1
        stmt = stmts[0]
        assert isinstance(stmt, DefineAgentStmt)
        assert stmt.name == "searcher"

    def test_define_agent_multiple(self):
        stmts = _parse("define agent searcher. define agent writer.")
        assert len(stmts) == 2
        assert isinstance(stmts[0], DefineAgentStmt)
        assert isinstance(stmts[1], DefineAgentStmt)
        assert stmts[0].name == "searcher"
        assert stmts[1].name == "writer"

    def test_define_missing_agent_keyword(self):
        with pytest.raises(ParseError, match="Expected 'agent'"):
            _parse("define something.")

    def test_define_agent_missing_name(self):
        with pytest.raises(ParseError):
            _parse("define agent.")


# ---------------------------------------------------------------------------
# tell (simple form)
# ---------------------------------------------------------------------------

class TestTellSimple:

    def test_tell_text(self):
        stmts = _parse("tell searcher text, hello world.")
        assert len(stmts) == 1
        stmt = stmts[0]
        assert isinstance(stmt, TellStmt)
        assert stmt.agent == "searcher"
        assert isinstance(stmt.message, TextLiteral)
        assert stmt.message.value == "hello world"
        assert stmt.body is None

    def test_tell_variable(self):
        stmts = _parse("tell writer myvar.")
        assert len(stmts) == 1
        stmt = stmts[0]
        assert isinstance(stmt, TellStmt)
        assert stmt.agent == "writer"
        assert isinstance(stmt.message, VarRef)
        assert stmt.message.name == "myvar"

    def test_tell_number(self):
        stmts = _parse("tell agent 42.")
        stmt = stmts[0]
        assert isinstance(stmt, TellStmt)
        assert isinstance(stmt.message, NumberLiteral)


# ---------------------------------------------------------------------------
# tell (block form)
# ---------------------------------------------------------------------------

class TestTellBlock:

    def test_tell_block_basic(self):
        src = """
        tell searcher.
          set intent to text, search.
          set query to text, python docs.
        end.
        """
        stmts = _parse(src)
        assert len(stmts) == 1
        stmt = stmts[0]
        assert isinstance(stmt, TellStmt)
        assert stmt.agent == "searcher"
        assert stmt.message is None
        assert stmt.body is not None
        assert len(stmt.body) == 2
        assert isinstance(stmt.body[0], SetStmt)
        assert isinstance(stmt.body[1], SetStmt)
        assert stmt.body[0].name == "intent"
        assert stmt.body[1].name == "query"

    def test_tell_block_single_set(self):
        src = "tell agent. set x to 5. end."
        stmts = _parse(src)
        stmt = stmts[0]
        assert isinstance(stmt, TellStmt)
        assert len(stmt.body) == 1

    def test_tell_block_unterminated(self):
        with pytest.raises(ParseError, match="Unterminated 'tell'"):
            _parse("tell searcher. set x to 5.")


# ---------------------------------------------------------------------------
# hear
# ---------------------------------------------------------------------------

class TestHear:

    def test_hear_basic(self):
        stmts = _parse("hear from searcher as result.")
        assert len(stmts) == 1
        stmt = stmts[0]
        assert isinstance(stmt, HearStmt)
        assert stmt.agent == "searcher"
        assert stmt.var_name == "result"
        assert stmt.timeout is None

    def test_hear_with_timeout(self):
        stmts = _parse("hear from writer as reply within 30 seconds.")
        stmt = stmts[0]
        assert isinstance(stmt, HearStmt)
        assert stmt.agent == "writer"
        assert stmt.var_name == "reply"
        assert isinstance(stmt.timeout, NumberLiteral)
        assert stmt.timeout.value == 30


# ---------------------------------------------------------------------------
# open/close chat
# ---------------------------------------------------------------------------

class TestOpenChat:

    def test_open_chat_basic(self):
        src = """
        open chat research.
          tell searcher text, find stuff.
          hear from searcher as result.
        close chat.
        """
        stmts = _parse(src)
        assert len(stmts) == 1
        stmt = stmts[0]
        assert isinstance(stmt, OpenChatStmt)
        assert stmt.name == "research"
        assert len(stmt.body) == 2
        assert isinstance(stmt.body[0], TellStmt)
        assert isinstance(stmt.body[1], HearStmt)

    def test_open_chat_with_control_flow(self):
        src = """
        open chat session.
          tell agent text, hello.
          hear from agent as reply.
          set ok to text, success.
          if the status of reply is ok then
            say the payload of reply.
          end.
        close chat.
        """
        stmts = _parse(src)
        assert len(stmts) == 1
        chat = stmts[0]
        assert isinstance(chat, OpenChatStmt)
        assert len(chat.body) == 4
        assert isinstance(chat.body[3], IfStmt)

    def test_open_chat_unterminated(self):
        with pytest.raises(ParseError, match="Unterminated 'open chat'"):
            _parse("open chat session. tell agent text, hi.")


# ---------------------------------------------------------------------------
# ResponseFieldExpr
# ---------------------------------------------------------------------------

class TestResponseFieldExpr:

    def test_payload_of(self):
        stmts = _parse("say the payload of result.")
        assert len(stmts) == 1
        say = stmts[0]
        assert isinstance(say, SayStmt)
        expr = say.values[0]
        assert isinstance(expr, ResponseFieldExpr)
        assert expr.field == "payload"
        assert isinstance(expr.target, VarRef)
        assert expr.target.name == "result"

    def test_status_of(self):
        stmts = _parse("say the status of myreply.")
        expr = stmts[0].values[0]
        assert isinstance(expr, ResponseFieldExpr)
        assert expr.field == "status"

    def test_tokens_of(self):
        stmts = _parse("say the tokens of result.")
        expr = stmts[0].values[0]
        assert isinstance(expr, ResponseFieldExpr)
        assert expr.field == "tokens"

    def test_model_of(self):
        stmts = _parse("say the model of result.")
        expr = stmts[0].values[0]
        assert isinstance(expr, ResponseFieldExpr)
        assert expr.field == "model"

    def test_error_of(self):
        stmts = _parse("say the error of result.")
        expr = stmts[0].values[0]
        assert isinstance(expr, ResponseFieldExpr)
        assert expr.field == "error"

    def test_length_of_still_works(self):
        stmts = _parse("say the length of myvar.")
        from cfe.parser import LengthExpr
        expr = stmts[0].values[0]
        assert isinstance(expr, LengthExpr)

    def test_response_field_in_comparison(self):
        src = "set ok to text, success. if the status of reply is ok then say text, ok. end."
        stmts = _parse(src)
        assert isinstance(stmts[0], SetStmt)
        assert isinstance(stmts[1], IfStmt)

    def test_response_field_in_arithmetic(self):
        src = "set total to the tokens of a plus the tokens of b."
        stmts = _parse(src)
        stmt = stmts[0]
        assert isinstance(stmt, SetStmt)


# ---------------------------------------------------------------------------
# Integration with existing syntax
# ---------------------------------------------------------------------------

class TestAgentInControlFlow:

    def test_tell_hear_inside_if(self):
        src = """
        if x is 5 then
          tell agent text, hello.
          hear from agent as reply.
        end.
        """
        stmts = _parse(src)
        assert isinstance(stmts[0], IfStmt)
        assert isinstance(stmts[0].then_body[0], TellStmt)
        assert isinstance(stmts[0].then_body[1], HearStmt)

    def test_tell_hear_inside_while(self):
        src = """
        while counter is less than 3 do
          tell agent text, go.
          hear from agent as reply.
          set counter to counter plus 1.
        end.
        """
        stmts = _parse(src)
        assert isinstance(stmts[0], WhileStmt)
        assert isinstance(stmts[0].body[0], TellStmt)
        assert isinstance(stmts[0].body[1], HearStmt)

    def test_full_agent_script(self):
        src = """
        define agent searcher.
        define agent writer.
        open chat tutorial.
          tell searcher.
            set intent to text, search.
            set query to text, python docs.
          end.
          hear from searcher as result.
          set err to text, error.
          if the status of result is err then
            say text, failed.
          else
            say the payload of result.
          end.
        close chat.
        """
        stmts = _parse(src)
        assert isinstance(stmts[0], DefineAgentStmt)
        assert isinstance(stmts[1], DefineAgentStmt)
        assert isinstance(stmts[2], OpenChatStmt)
        chat = stmts[2]
        assert len(chat.body) == 4
        assert isinstance(chat.body[0], TellStmt)
        assert isinstance(chat.body[1], HearStmt)
        assert isinstance(chat.body[2], SetStmt)
        assert isinstance(chat.body[3], IfStmt)
