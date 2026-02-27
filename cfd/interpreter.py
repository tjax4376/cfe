"""
CFD v2 Interpreter – walks the AST and executes statements.

Version: 2.1
Author: Generated for aidev
Change rationale: Phase 2 – while loops, for-each range iteration, stop (break)
                  and skip (continue) via exception-based loop signals.

The interpreter keeps a flat ``env`` dict (symbol table).  Scoping will be
added when functions arrive in Phase 3.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional

from .parser import (
    AskStmt,
    BinaryExpr,
    BoolLiteral,
    DecimalLiteral,
    Expr,
    ForEachStmt,
    IfStmt,
    LengthExpr,
    NoneLiteral,
    NumberLiteral,
    RepeatStmt,
    SayStmt,
    SetStmt,
    SkipStmt,
    Stmt,
    StopStmt,
    TextLiteral,
    UnaryExpr,
    VarRef,
    WhileStmt,
)
from .typesystem import coerce_numeric_pair, to_text, to_truth

MAX_LOOP_ITERATIONS = 1_000_000


class CfdRuntimeError(Exception):
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

    raise CfdRuntimeError(f"Unknown expression node {type(node).__name__}", node.line)


def _eval_unary(node: UnaryExpr, env: Dict[str, Any]) -> Any:
    val = _eval_expr(node.operand, env)
    if node.op == "negative":
        if isinstance(val, (int, float)):
            return -val
        raise CfdRuntimeError(
            f"Cannot negate {to_text(val)!r}", node.line,
        )
    if node.op == "not":
        return not to_truth(val)
    raise CfdRuntimeError(f"Unknown unary op {node.op!r}", node.line)


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

    raise CfdRuntimeError(f"Unknown binary op {op!r}", node.line)


def _eval_arithmetic(op: str, left: Any, right: Any, line: int) -> Any:
    try:
        lv, rv = coerce_numeric_pair(left, right)
    except TypeError:
        raise CfdRuntimeError(
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
            raise CfdRuntimeError("Division by zero", line)
        if isinstance(lv, int) and isinstance(rv, int):
            return lv // rv
        return lv / rv
    if op == "modulo":
        if rv == 0:
            raise CfdRuntimeError("Modulo by zero", line)
        return lv % rv
    raise CfdRuntimeError(f"Unknown arithmetic op {op!r}", line)


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

    raise CfdRuntimeError(f"Unknown comparison op {op!r}", line)


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
        raise CfdRuntimeError("'stop' used outside of a loop", sig.line) from None
    except _SkipSignal as sig:
        raise CfdRuntimeError("'skip' used outside of a loop", sig.line) from None


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
            raise CfdRuntimeError(
                f"repeat count must be a number, got {to_text(n_val)!r}",
                stmt.line,
            )
        n = int(n_val)
        if n > MAX_LOOP_ITERATIONS:
            raise CfdRuntimeError(
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
                    raise CfdRuntimeError(
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
            raise CfdRuntimeError("'for each' start must be a number", stmt.line)
        if not isinstance(end_val, (int, float)):
            raise CfdRuntimeError("'for each' end must be a number", stmt.line)
        if not isinstance(step_val, (int, float)):
            raise CfdRuntimeError("'for each' step must be a number", stmt.line)
        if step_val == 0:
            raise CfdRuntimeError("'for each' step cannot be zero", stmt.line)

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
            raise CfdRuntimeError(
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

    raise CfdRuntimeError(f"Unknown statement {type(stmt).__name__}", stmt.line)
