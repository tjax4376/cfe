"""
CFE v2 Lexer – tokenises .cfe source into a flat token stream.

Version: 2.0
Author: Generated for aidev
Change rationale: Phase 1 rewrite – fix newline handling, keep tokens minimal
                  (WORD, PERIOD, COMMA). Text-literal detection is handled by
                  the parser (it sees WORD("text") + COMMA and enters text mode).
                  Decimals like ``3 point 14`` are three WORD tokens; the parser
                  folds them into a single DecimalLiteral node.

Token kinds
-----------
WORD   – a run of ASCII letters OR a run of ASCII digits.
PERIOD – the ``.`` character (statement terminator).
COMMA  – the ``,`` character (separator / text delimiter).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class TokenKind(Enum):
    WORD = auto()
    PERIOD = auto()
    COMMA = auto()


@dataclass(slots=True)
class Token:
    kind: TokenKind
    value: str
    line: int
    col: int

    def __repr__(self) -> str:
        return f"Token({self.kind.name}, {self.value!r}, L{self.line}:{self.col})"


_WORD_RE = re.compile(r"[a-zA-Z]+|[0-9]+")


class LexError(Exception):
    def __init__(self, msg: str, line: int, col: int) -> None:
        self.line = line
        self.col = col
        super().__init__(f"Lex error at line {line}, col {col}: {msg}")


def lex(source: str) -> List[Token]:
    """Tokenise *source* into a list of ``Token`` objects.

    Whitespace (space, tab, newline, carriage-return) is skipped.
    Only three token kinds are emitted: WORD, PERIOD, COMMA.
    Any character that is not whitespace, a letter, a digit, a period, or a
    comma raises ``LexError``.
    """
    tokens: List[Token] = []
    line = 1
    col = 1
    i = 0
    n = len(source)

    while i < n:
        c = source[i]

        if c in " \t\r":
            col += 1
            i += 1
            continue

        if c == "\n":
            line += 1
            col = 1
            i += 1
            continue

        if c == ".":
            tokens.append(Token(TokenKind.PERIOD, ".", line, col))
            col += 1
            i += 1
            continue

        if c == ",":
            tokens.append(Token(TokenKind.COMMA, ",", line, col))
            col += 1
            i += 1
            continue

        m = _WORD_RE.match(source, i)
        if m:
            word = m.group(0)
            tokens.append(Token(TokenKind.WORD, word, line, col))
            col += len(word)
            i = m.end()
            continue

        raise LexError(f"Unexpected character {c!r}", line, col)

    return tokens
