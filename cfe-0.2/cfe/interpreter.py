"""
CFE v3 Interpreter – walks the AST and executes statements.

Version: 3.0
Author: Generated for aidev
Change rationale: Phase 9a – agent communication primitives (define agent,
                  tell, hear, open/close chat, response field access).

The interpreter keeps a flat ``env`` dict (symbol table).  Scoping will be
added when functions arrive in Phase 3.  Agent communication is delegated
to the gateway module (cfe.agent.gateway).
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional

from .parser import (
    AskStmt,
    BinaryExpr,
    BoolLiteral,
    DecimalLiteral,
    DefineAgentStmt,
    Expr,
    ForEachStmt,
    HearStmt,
    IfStmt,
    LengthExpr,
    NoneLiteral,
    NumberLiteral,
    OpenChatStmt,
    RepeatStmt,
    ResponseFieldExpr,
    SayStmt,
    SetStmt,
    SkipStmt,
    Stmt,
    StopStmt,
    TellStmt,
    TextLiteral,
    UnaryExpr,
    VarRef,
    WhileStmt,
)
from .typesystem import coerce_numeric_pair, to_text, to_truth

MAX_LOOP_ITERATIONS = 1_000_000

_gateway = None


def _get_gateway():
    """Lazy-load the gateway to avoid circular imports and allow headless use."""
    global _gateway
    if _gateway is None:
        from cfe.agent.gateway import Gateway
        _gateway = Gateway()
    return _gateway


def set_gateway(gw) -> None:
    """Inject a gateway instance (used by tests and the CLI)."""
    global _gateway
    _gateway = gw


def get_gateway():
    """Return the current gateway instance, creating one if needed."""
    return _get_gateway()


class CfeRuntimeError(Exception):
    def __init__(self, msg: str, line: int = 0) -> None:
        self.line = line
        super().__init__(f"Runtime error at line {line}: {msg}")


class _LoopSignal(Exception):
    """Internal signal for loop control flow (not a user-facing error)."""
    def __init__(self, line: int = 0) -> None:
        self.line = line
        super().__init__()


class _StopSignal(_LoopSignal):
    """Raised by ``stop.`` to break out of the innermost loop."""


class _SkipSignal(_LoopSignal):
    """Raised by ``skip.`` to jump to the next loop iteration."""


# ---------------------------------------------------------------------------
# Expression evaluator
# ---------------------------------------------------------------------------

def _eval_expr(node: Expr, env: Dict[str, Any]) -> Any:
    """Recursively evaluate an expression AST node and return a Python value."""

    if isinstance(node, NumberLiteral):
        return node.value

    if isinstance(node, DecimalLiteral):
        return node.value

    if isinstance(node, TextLiteral):
        return node.value

    if isinstance(node, BoolLiteral):
        return node.value

    if isinstance(node, NoneLiteral):
        return None

    if isinstance(node, VarRef):
        if node.name in env:
            return env[node.name]
        return node.name

    if isinstance(node, UnaryExpr):
        return _eval_unary(node, env)

    if isinstance(node, BinaryExpr):
        return _eval_binary(node, env)

    if isinstance(node, LengthExpr):
        operand = _eval_expr(node.operand, env)
        text = to_text(operand)
        return len(text)

    if isinstance(node, ResponseFieldExpr):
        return _eval_response_field(node, env)

    raise CfeRuntimeError(f"Unknown expression node {type(node).__name__}", node.line)


def _eval_unary(node: UnaryExpr, env: Dict[str, Any]) -> Any:
    val = _eval_expr(node.operand, env)
    if node.op == "negative":
        if isinstance(val, (int, float)):
            return -val
        raise CfeRuntimeError(
            f"Cannot negate {to_text(val)!r}", node.line,
        )
    if node.op == "not":
        return not to_truth(val)
    raise CfeRuntimeError(f"Unknown unary op {node.op!r}", node.line)


def _eval_binary(node: BinaryExpr, env: Dict[str, Any]) -> Any:
    op = node.op

    # Short-circuit logic
    if op == "and":
        left = _eval_expr(node.left, env)
        if not to_truth(left):
            return False
        return to_truth(_eval_expr(node.right, env))

    if op == "or":
        left = _eval_expr(node.left, env)
        if to_truth(left):
            return True
        return to_truth(_eval_expr(node.right, env))

    left = _eval_expr(node.left, env)
    right = _eval_expr(node.right, env)

    # String join
    if op == "joined with":
        return to_text(left) + to_text(right)

    # Arithmetic
    if op in ("plus", "minus", "times", "divided by", "modulo"):
        return _eval_arithmetic(op, left, right, node.line)

    # Comparisons
    if op.startswith("is"):
        return _eval_comparison(op, left, right, node.line)

    raise CfeRuntimeError(f"Unknown binary op {op!r}", node.line)


def _eval_arithmetic(op: str, left: Any, right: Any, line: int) -> Any:
    try:
        lv, rv = coerce_numeric_pair(left, right)
    except TypeError:
        raise CfeRuntimeError(
            f"Cannot do arithmetic on {to_text(left)!r} and {to_text(right)!r}",
            line,
        )
    if op == "plus":
        return lv + rv
    if op == "minus":
        return lv - rv
    if op == "times":
        return lv * rv
    if op == "divided by":
        if rv == 0:
            raise CfeRuntimeError("Division by zero", line)
        if isinstance(lv, int) and isinstance(rv, int):
            return lv // rv
        return lv / rv
    if op == "modulo":
        if rv == 0:
            raise CfeRuntimeError("Modulo by zero", line)
        return lv % rv
    raise CfeRuntimeError(f"Unknown arithmetic op {op!r}", line)


def _eval_comparison(op: str, left: Any, right: Any, line: int) -> bool:
    if op == "is":
        return left == right
    if op == "is not":
        return left != right

    try:
        lv, rv = coerce_numeric_pair(left, right)
    except TypeError:
        lv, rv = to_text(left), to_text(right)

    if op == "is greater than":
        return lv > rv
    if op == "is less than":
        return lv < rv
    if op == "is at least":
        return lv >= rv
    if op == "is at most":
        return lv <= rv

    raise CfeRuntimeError(f"Unknown comparison op {op!r}", line)


# ---------------------------------------------------------------------------
# Response field access
# ---------------------------------------------------------------------------

def _eval_response_field(node: ResponseFieldExpr, env: Dict[str, Any]) -> Any:
    target = _eval_expr(node.target, env)
    from cfe.agent.message import Response
    if not isinstance(target, Response):
        raise CfeRuntimeError(
            f"Cannot access field '{node.field}' – value is not an agent response",
            node.line,
        )
    try:
        return target.get_field(node.field)
    except KeyError:
        raise CfeRuntimeError(
            f"Unknown response field '{node.field}'", node.line,
        )


# ---------------------------------------------------------------------------
# Statement executor
# ---------------------------------------------------------------------------

def run(stmts: List[Stmt], env: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute a list of statement AST nodes.  Returns the environment dict."""
    if env is None:
        env = {}
    for stmt in stmts:
        _exec_stmt(stmt, env)
    return env


def execute(stmts: List[Stmt], env: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Top-level entry point – catches stray loop-control signals."""
    try:
        return run(stmts, env)
    except _StopSignal as sig:
        raise CfeRuntimeError("'stop' used outside of a loop", sig.line) from None
    except _SkipSignal as sig:
        raise CfeRuntimeError("'skip' used outside of a loop", sig.line) from None


def _exec_stmt(stmt: Stmt, env: Dict[str, Any]) -> None:

    if isinstance(stmt, SetStmt):
        env[stmt.name] = _eval_expr(stmt.value, env)
        return

    if isinstance(stmt, SayStmt):
        parts = [to_text(_eval_expr(v, env)) for v in stmt.values]
        print(" ".join(parts))
        return

    if isinstance(stmt, AskStmt):
        try:
            line_in = input()
        except EOFError:
            line_in = ""
        try:
            env[stmt.name] = int(line_in)
        except ValueError:
            try:
                env[stmt.name] = float(line_in)
            except ValueError:
                env[stmt.name] = line_in
        return

    if isinstance(stmt, IfStmt):
        cond = _eval_expr(stmt.condition, env)
        if to_truth(cond):
            run(stmt.then_body, env)
        else:
            run(stmt.else_body, env)
        return

    if isinstance(stmt, RepeatStmt):
        n_val = _eval_expr(stmt.count, env)
        if not isinstance(n_val, (int, float)):
            raise CfeRuntimeError(
                f"repeat count must be a number, got {to_text(n_val)!r}",
                stmt.line,
            )
        n = int(n_val)
        if n > MAX_LOOP_ITERATIONS:
            raise CfeRuntimeError(
                f"Loop count {n} exceeds maximum ({MAX_LOOP_ITERATIONS})",
                stmt.line,
            )
        try:
            for _ in range(n):
                try:
                    run(stmt.body, env)
                except _SkipSignal:
                    continue
        except _StopSignal:
            pass
        return

    if isinstance(stmt, WhileStmt):
        iterations = 0
        try:
            while to_truth(_eval_expr(stmt.condition, env)):
                iterations += 1
                if iterations > MAX_LOOP_ITERATIONS:
                    raise CfeRuntimeError(
                        f"While loop exceeded maximum iterations ({MAX_LOOP_ITERATIONS})",
                        stmt.line,
                    )
                try:
                    run(stmt.body, env)
                except _SkipSignal:
                    continue
        except _StopSignal:
            pass
        return

    if isinstance(stmt, ForEachStmt):
        start_val = _eval_expr(stmt.start, env)
        end_val = _eval_expr(stmt.end, env)
        step_val: Any = 1
        if stmt.step is not None:
            step_val = _eval_expr(stmt.step, env)

        if not isinstance(start_val, (int, float)):
            raise CfeRuntimeError("'for each' start must be a number", stmt.line)
        if not isinstance(end_val, (int, float)):
            raise CfeRuntimeError("'for each' end must be a number", stmt.line)
        if not isinstance(step_val, (int, float)):
            raise CfeRuntimeError("'for each' step must be a number", stmt.line)
        if step_val == 0:
            raise CfeRuntimeError("'for each' step cannot be zero", stmt.line)

        if isinstance(start_val, float) or isinstance(end_val, float) or isinstance(step_val, float):
            start_val, end_val, step_val = float(start_val), float(end_val), float(step_val)

        values: list[Any] = []
        current = start_val
        if step_val > 0:
            while current <= end_val:
                values.append(current)
                current += step_val
        else:
            while current >= end_val:
                values.append(current)
                current += step_val

        if len(values) > MAX_LOOP_ITERATIONS:
            raise CfeRuntimeError(
                f"For-each range produces {len(values)} iterations, "
                f"exceeding maximum ({MAX_LOOP_ITERATIONS})",
                stmt.line,
            )

        try:
            for val in values:
                env[stmt.var_name] = val
                try:
                    run(stmt.body, env)
                except _SkipSignal:
                    continue
        except _StopSignal:
            pass
        return

    if isinstance(stmt, StopStmt):
        raise _StopSignal(stmt.line)

    if isinstance(stmt, SkipStmt):
        raise _SkipSignal(stmt.line)

    if isinstance(stmt, DefineAgentStmt):
        _exec_define_agent(stmt)
        return

    if isinstance(stmt, OpenChatStmt):
        _exec_open_chat(stmt, env)
        return

    if isinstance(stmt, TellStmt):
        _exec_tell(stmt, env)
        return

    if isinstance(stmt, HearStmt):
        _exec_hear(stmt, env)
        return

    raise CfeRuntimeError(f"Unknown statement {type(stmt).__name__}", stmt.line)


# ---------------------------------------------------------------------------
# Agent statement executors
# ---------------------------------------------------------------------------

def _exec_define_agent(stmt: DefineAgentStmt) -> None:
    from cfe.agent.gateway import GatewayError
    gw = _get_gateway()
    try:
        gw.declare_agent(stmt.name)
    except GatewayError as exc:
        raise CfeRuntimeError(str(exc), stmt.line) from None


def _exec_open_chat(stmt: OpenChatStmt, env: Dict[str, Any]) -> None:
    from cfe.agent.session import SessionError
    gw = _get_gateway()
    try:
        gw.open_chat(stmt.name)
    except SessionError as exc:
        raise CfeRuntimeError(str(exc), stmt.line) from None
    try:
        run(stmt.body, env)
    finally:
        try:
            gw.close_chat(stmt.name)
        except SessionError:
            pass


def _exec_tell(stmt: TellStmt, env: Dict[str, Any]) -> None:
    from cfe.agent.message import Message
    gw = _get_gateway()

    if not gw.is_declared(stmt.agent):
        raise CfeRuntimeError(
            f"Agent '{stmt.agent}' has not been declared with 'define agent'",
            stmt.line,
        )

    if stmt.message is not None:
        text = to_text(_eval_expr(stmt.message, env))
        message = Message(
            agent_name=stmt.agent,
            text=text,
        )
    elif stmt.body is not None:
        payload: Dict[str, Any] = {}
        for body_stmt in stmt.body:
            if isinstance(body_stmt, SetStmt):
                payload[body_stmt.name] = _eval_expr(body_stmt.value, env)
            else:
                raise CfeRuntimeError(
                    "Only 'set' statements are allowed inside a 'tell' block",
                    body_stmt.line,
                )
        message = Message(
            agent_name=stmt.agent,
            payload=payload,
        )
    else:
        raise CfeRuntimeError(
            "'tell' must have either a message expression or a block body",
            stmt.line,
        )

    response = gw.send(message)
    env[f"_last_response_{stmt.agent}"] = response


def _exec_hear(stmt: HearStmt, env: Dict[str, Any]) -> None:
    from cfe.agent.message import Response
    gw = _get_gateway()

    if not gw.is_declared(stmt.agent):
        raise CfeRuntimeError(
            f"Agent '{stmt.agent}' has not been declared with 'define agent'",
            stmt.line,
        )

    response_key = f"_last_response_{stmt.agent}"
    response = env.get(response_key)
    if response is None or not isinstance(response, Response):
        raise CfeRuntimeError(
            f"No pending response from agent '{stmt.agent}'. "
            f"Did you 'tell' the agent first?",
            stmt.line,
        )

    env[stmt.var_name] = response
    del env[response_key]
