"""
CFD v2 Type System – runtime value types and coercion rules.

Version: 2.0
Author: Generated for aidev
Change rationale: Phase 1 – define Number, Decimal, Text, Truth, NoneType;
                  runtime coercion helpers for the interpreter.

Design note: values at runtime are plain Python objects (int, float, str,
bool, None).  This module provides helpers that the interpreter and a future
type-checker / compiler can share.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Any


class CfdType(Enum):
    NUMBER = auto()
    DECIMAL = auto()
    TEXT = auto()
    TRUTH = auto()
    NONE = auto()


def type_of(value: Any) -> CfdType:
    """Return the CFD type for a runtime Python value."""
    if value is None:
        return CfdType.NONE
    if isinstance(value, bool):
        return CfdType.TRUTH
    if isinstance(value, int):
        return CfdType.NUMBER
    if isinstance(value, float):
        return CfdType.DECIMAL
    if isinstance(value, str):
        return CfdType.TEXT
    raise TypeError(f"Unknown CFD value type: {type(value).__name__}")


def type_name(t: CfdType) -> str:
    """Human-readable name for display in error messages."""
    return {
        CfdType.NUMBER: "number",
        CfdType.DECIMAL: "decimal",
        CfdType.TEXT: "text",
        CfdType.TRUTH: "truth",
        CfdType.NONE: "none",
    }[t]


# -- Coercion rules ---------------------------------------------------------

def to_number(value: Any) -> int:
    """Coerce *value* to an integer, or raise."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            pass
    raise TypeError(f"Cannot convert {type_name(type_of(value))} to number")


def to_decimal(value: Any) -> float:
    """Coerce *value* to a float, or raise."""
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            pass
    raise TypeError(f"Cannot convert {type_name(type_of(value))} to decimal")


def to_text(value: Any) -> str:
    """Coerce any value to its text representation."""
    if value is None:
        return "none"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return str(value)
    return str(value)


def to_truth(value: Any) -> bool:
    """Coerce *value* to a boolean (truthiness)."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, float):
        return value != 0.0
    if isinstance(value, str):
        return len(value) > 0
    return bool(value)


def coerce_numeric_pair(left: Any, right: Any) -> tuple[Any, Any]:
    """Promote both operands to a common numeric type.

    - int, int → int, int
    - int, float (or vice-versa) → float, float
    """
    if isinstance(left, float) or isinstance(right, float):
        return to_decimal(left), to_decimal(right)
    return to_number(left), to_number(right)
