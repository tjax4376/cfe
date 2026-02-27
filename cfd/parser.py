"""
CFD v2 Parser – builds an AST from the token stream.

Version: 2.1
Author: Generated for aidev
Change rationale: Phase 2 – while loops, for-each range iteration, stop (break)
                  and skip (continue) loop control.

Expression grammar (precedence low → high)
------------------------------------------
expr        = or_expr
or_expr     = and_expr ( "or" and_expr )*
and_expr    = not_expr ( "and" not_expr )*
not_expr    = "not" not_expr | cmp_expr
cmp_expr    = add_expr ( cmp_op add_expr )?
add_expr    = mul_expr ( ("plus"|"minus") mul_expr )*
mul_expr    = unary    ( ("times"|"divided" "by"|"modulo") unary )*
unary       = "negative" unary | postfix
postfix     = atom ( "joined" "with" atom )*
atom        = NUMBER | NUMBER "point" NUMBER
            | "true" | "false" | "none"
            | "text" COMMA <words until comma/period>
            | "the" "length" "of" atom
            | IDENT                          (variable reference)

cmp_op      = "is" "not"
            | "is" "greater" "than"
            | "is" "less" "than"
            | "is" "at" "least"
            | "is" "at" "most"
            | "is"

Statements
----------
set <name> to <expr>.
say <expr> , <expr> , ... .
ask <name>.
if <expr> then <stmts> [ else <stmts> ] end.
repeat <expr> times <stmts> end.
while <expr> do <stmts> end.
for each <name> from <expr> to <expr> [by <expr>] do <stmts> end.
stop.
skip.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union

from .lexer import Token, TokenKind


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ParseError(Exception):
    def __init__(self, msg: str, line: int = 0, col: int = 0) -> None:
        self.line = line
        self.col = col
        super().__init__(f"Parse error at line {line}, col {col}: {msg}")


# ---------------------------------------------------------------------------
# AST – Expressions
# ---------------------------------------------------------------------------

@dataclass
class Expr:
    """Base for all expression nodes."""
    line: int


@dataclass
class NumberLiteral(Expr):
    value: int


@dataclass
class DecimalLiteral(Expr):
    value: float


@dataclass
class TextLiteral(Expr):
    value: str


@dataclass
class BoolLiteral(Expr):
    value: bool


@dataclass
class NoneLiteral(Expr):
    pass


@dataclass
class VarRef(Expr):
    name: str


@dataclass
class BinaryExpr(Expr):
    op: str
    left: Expr
    right: Expr


@dataclass
class UnaryExpr(Expr):
    op: str
    operand: Expr


@dataclass
class LengthExpr(Expr):
    operand: Expr


# ---------------------------------------------------------------------------
# AST – Statements
# ---------------------------------------------------------------------------

@dataclass
class Stmt:
    """Base for all statement nodes."""
    line: int


@dataclass
class SetStmt(Stmt):
    name: str
    value: Expr


@dataclass
class SayStmt(Stmt):
    values: List[Expr]


@dataclass
class AskStmt(Stmt):
    name: str


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_body: List[Stmt]
    else_body: List[Stmt]


@dataclass
class RepeatStmt(Stmt):
    count: Expr
    body: List[Stmt]


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: List[Stmt]


@dataclass
class ForEachStmt(Stmt):
    var_name: str
    start: Expr
    end: Expr
    step: Optional[Expr]
    body: List[Stmt]


@dataclass
class StopStmt(Stmt):
    pass


@dataclass
class SkipStmt(Stmt):
    pass


# GUI stubs (un-wired; kept so later phases can activate them)
@dataclass
class CreateWindowStmt(Stmt):
    name: str
    title: str
    parent: Optional[str] = None

@dataclass
class AddLabelStmt(Stmt):
    text: str

@dataclass
class AddCloseButtonStmt(Stmt):
    pass

@dataclass
class ShowWindowsStmt(Stmt):
    pass


# ---------------------------------------------------------------------------
# Token-stream helpers
# ---------------------------------------------------------------------------

STRUCTURAL_KEYWORDS = frozenset({
    "then", "else", "end", "times", "do",
})

COMPARISON_STARTERS = frozenset({
    "is",
})

EXPR_KEYWORDS = frozenset({
    "plus", "minus", "times", "divided", "modulo",
    "and", "or", "not", "negative",
    "is", "joined", "the", "text",
    "true", "false", "none", "point",
    "by", "with", "greater", "than", "less", "at", "least", "most",
    "of", "length", "each", "from", "to",
})

STATEMENT_KEYWORDS = frozenset({
    "set", "say", "ask", "if", "repeat",
    "while", "for", "stop", "skip",
    "create", "add", "show",
})


class _Parser:
    """Recursive-descent parser with Pratt-style precedence for expressions."""

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
        self._stop_words: frozenset[str] = frozenset()

    # -- Utilities ----------------------------------------------------------

    def _at_end(self) -> bool:
        return self.pos >= len(self.tokens)

    def _peek(self) -> Token:
        if self._at_end():
            last = self.tokens[-1] if self.tokens else Token(TokenKind.PERIOD, ".", 0, 0)
            raise ParseError("Unexpected end of input", last.line, last.col)
        return self.tokens[self.pos]

    def _peek_safe(self) -> Optional[Token]:
        if self._at_end():
            return None
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        t = self._peek()
        self.pos += 1
        return t

    def _check_word(self, value: str) -> bool:
        t = self._peek_safe()
        return t is not None and t.kind == TokenKind.WORD and t.value.lower() == value

    def _check_kind(self, kind: TokenKind) -> bool:
        t = self._peek_safe()
        return t is not None and t.kind == kind

    def _expect_word(self, value: str) -> Token:
        t = self._advance()
        if t.kind != TokenKind.WORD or t.value.lower() != value:
            raise ParseError(f"Expected '{value}', got {t.value!r}", t.line, t.col)
        return t

    def _expect_kind(self, kind: TokenKind) -> Token:
        t = self._advance()
        if t.kind != kind:
            raise ParseError(f"Expected {kind.name}, got {t.value!r}", t.line, t.col)
        return t

    def _at_expr_boundary(self) -> bool:
        """True when the next token cannot continue the current expression."""
        t = self._peek_safe()
        if t is None:
            return True
        if t.kind in (TokenKind.PERIOD, TokenKind.COMMA):
            return True
        if t.kind == TokenKind.WORD:
            low = t.value.lower()
            if low in STRUCTURAL_KEYWORDS or low in self._stop_words:
                return True
        return False

    # -- Expression parsing (precedence climbing) ---------------------------

    def _parse_expr(self) -> Expr:
        return self._parse_or()

    def _parse_or(self) -> Expr:
        left = self._parse_and()
        while self._check_word("or"):
            self._advance()
            right = self._parse_and()
            left = BinaryExpr(line=left.line, op="or", left=left, right=right)
        return left

    def _parse_and(self) -> Expr:
        left = self._parse_not()
        while self._check_word("and"):
            self._advance()
            right = self._parse_not()
            left = BinaryExpr(line=left.line, op="and", left=left, right=right)
        return left

    def _parse_not(self) -> Expr:
        if self._check_word("not"):
            t = self._advance()
            operand = self._parse_not()
            return UnaryExpr(line=t.line, op="not", operand=operand)
        return self._parse_comparison()

    def _parse_comparison(self) -> Expr:
        left = self._parse_add()
        if self._check_word("is"):
            line = self._peek().line
            self._advance()  # consume "is"
            op = self._resolve_cmp_op()
            right = self._parse_add()
            return BinaryExpr(line=line, op=op, left=left, right=right)
        return left

    def _resolve_cmp_op(self) -> str:
        if self._check_word("not"):
            self._advance()
            return "is not"
        if self._check_word("greater"):
            self._advance()
            self._expect_word("than")
            return "is greater than"
        if self._check_word("less"):
            self._advance()
            self._expect_word("than")
            return "is less than"
        if self._check_word("at"):
            self._advance()
            if self._check_word("least"):
                self._advance()
                return "is at least"
            if self._check_word("most"):
                self._advance()
                return "is at most"
            t = self._peek()
            raise ParseError(f"Expected 'least' or 'most' after 'at', got {t.value!r}", t.line, t.col)
        return "is"

    def _parse_add(self) -> Expr:
        left = self._parse_mul()
        while True:
            if self._check_word("plus"):
                self._advance()
                right = self._parse_mul()
                left = BinaryExpr(line=left.line, op="plus", left=left, right=right)
            elif self._check_word("minus"):
                self._advance()
                right = self._parse_mul()
                left = BinaryExpr(line=left.line, op="minus", left=left, right=right)
            else:
                break
        return left

    def _parse_mul(self) -> Expr:
        left = self._parse_unary()
        while True:
            if self._check_word("times") and "times" not in self._stop_words:
                self._advance()
                right = self._parse_unary()
                left = BinaryExpr(line=left.line, op="times", left=left, right=right)
            elif self._check_word("divided"):
                self._advance()
                self._expect_word("by")
                right = self._parse_unary()
                left = BinaryExpr(line=left.line, op="divided by", left=left, right=right)
            elif self._check_word("modulo"):
                self._advance()
                right = self._parse_unary()
                left = BinaryExpr(line=left.line, op="modulo", left=left, right=right)
            else:
                break
        return left

    def _parse_unary(self) -> Expr:
        if self._check_word("negative"):
            t = self._advance()
            operand = self._parse_unary()
            return UnaryExpr(line=t.line, op="negative", operand=operand)
        return self._parse_postfix()

    def _parse_postfix(self) -> Expr:
        left = self._parse_atom()
        while self._check_word("joined"):
            self._advance()
            self._expect_word("with")
            right = self._parse_atom()
            left = BinaryExpr(line=left.line, op="joined with", left=left, right=right)
        return left

    def _parse_atom(self) -> Expr:
        t = self._peek()

        # "the length of <expr>"
        if t.kind == TokenKind.WORD and t.value.lower() == "the":
            saved = self.pos
            self._advance()
            if self._check_word("length"):
                self._advance()
                self._expect_word("of")
                operand = self._parse_atom()
                return LengthExpr(line=t.line, operand=operand)
            self.pos = saved

        # text literal: text, <words until comma/period>
        if t.kind == TokenKind.WORD and t.value.lower() == "text":
            next_pos = self.pos + 1
            if next_pos < len(self.tokens) and self.tokens[next_pos].kind == TokenKind.COMMA:
                self._advance()  # consume "text"
                self._advance()  # consume ","
                return self._parse_text_literal(t.line)

        # boolean
        if t.kind == TokenKind.WORD and t.value.lower() == "true":
            self._advance()
            return BoolLiteral(line=t.line, value=True)
        if t.kind == TokenKind.WORD and t.value.lower() == "false":
            self._advance()
            return BoolLiteral(line=t.line, value=False)

        # none
        if t.kind == TokenKind.WORD and t.value.lower() == "none":
            self._advance()
            return NoneLiteral(line=t.line)

        # number or decimal (``42`` or ``3 point 14``)
        if t.kind == TokenKind.WORD and t.value.isdigit():
            self._advance()
            if self._check_word("point"):
                self._advance()
                frac_t = self._advance()
                if frac_t.kind != TokenKind.WORD or not frac_t.value.isdigit():
                    raise ParseError(
                        f"Expected digits after 'point', got {frac_t.value!r}",
                        frac_t.line, frac_t.col,
                    )
                return DecimalLiteral(
                    line=t.line,
                    value=float(f"{t.value}.{frac_t.value}"),
                )
            return NumberLiteral(line=t.line, value=int(t.value))

        # variable reference (any non-keyword word)
        if t.kind == TokenKind.WORD:
            low = t.value.lower()
            if low not in STRUCTURAL_KEYWORDS and low not in self._stop_words:
                self._advance()
                return VarRef(line=t.line, name=t.value)

        raise ParseError(f"Expected expression, got {t.value!r}", t.line, t.col)

    def _parse_text_literal(self, line: int) -> TextLiteral:
        """Collect words until the next COMMA or PERIOD token."""
        parts: List[str] = []
        while not self._at_end():
            t = self._peek()
            if t.kind in (TokenKind.COMMA, TokenKind.PERIOD):
                break
            if t.kind == TokenKind.WORD:
                parts.append(t.value)
                self._advance()
            else:
                break
        return TextLiteral(line=line, value=" ".join(parts))

    # -- Statement parsing ---------------------------------------------------

    def parse_program(self) -> List[Stmt]:
        stmts: List[Stmt] = []
        while not self._at_end():
            stmts.append(self._parse_statement())
        return stmts

    def _parse_statement(self) -> Stmt:
        t = self._peek()
        if t.kind != TokenKind.WORD:
            raise ParseError(f"Expected statement keyword, got {t.value!r}", t.line, t.col)

        word = t.value.lower()

        if word == "set":
            return self._parse_set()
        if word == "say":
            return self._parse_say()
        if word == "ask":
            return self._parse_ask()
        if word == "if":
            return self._parse_if()
        if word == "repeat":
            return self._parse_repeat()
        if word == "while":
            return self._parse_while()
        if word == "for":
            return self._parse_for_each()
        if word == "stop":
            return self._parse_stop()
        if word == "skip":
            return self._parse_skip()

        raise ParseError(f"Unknown statement keyword {t.value!r}", t.line, t.col)

    # -- set <name> to <expr>. ----------------------------------------------

    def _parse_set(self) -> SetStmt:
        t = self._advance()  # consume "set"
        name_tok = self._advance()
        if name_tok.kind != TokenKind.WORD:
            raise ParseError("Expected variable name after 'set'", name_tok.line, name_tok.col)
        self._expect_word("to")
        expr = self._parse_expr()
        self._expect_kind(TokenKind.PERIOD)
        return SetStmt(line=t.line, name=name_tok.value, value=expr)

    # -- say <expr>, <expr>, ... . ------------------------------------------

    def _parse_say(self) -> SayStmt:
        t = self._advance()  # consume "say"
        values: List[Expr] = []
        values.append(self._parse_expr())
        while self._check_kind(TokenKind.COMMA):
            self._advance()  # consume ","
            if self._check_kind(TokenKind.PERIOD):
                break
            values.append(self._parse_expr())
        self._expect_kind(TokenKind.PERIOD)
        return SayStmt(line=t.line, values=values)

    # -- ask <name>. --------------------------------------------------------

    def _parse_ask(self) -> AskStmt:
        t = self._advance()  # consume "ask"
        name_tok = self._advance()
        if name_tok.kind != TokenKind.WORD:
            raise ParseError("Expected variable name after 'ask'", name_tok.line, name_tok.col)
        self._expect_kind(TokenKind.PERIOD)
        return AskStmt(line=t.line, name=name_tok.value)

    # -- if <expr> then <stmts> [else <stmts>] end. ------------------------

    def _parse_if(self) -> IfStmt:
        t = self._advance()  # consume "if"
        condition = self._parse_expr()
        self._expect_word("then")
        then_body: List[Stmt] = []
        else_body: List[Stmt] = []
        while not self._at_end():
            if self._check_word("else"):
                self._advance()
                break
            if self._check_word("end"):
                self._advance()
                self._expect_kind(TokenKind.PERIOD)
                return IfStmt(line=t.line, condition=condition,
                              then_body=then_body, else_body=else_body)
            then_body.append(self._parse_statement())
        while not self._at_end():
            if self._check_word("end"):
                self._advance()
                self._expect_kind(TokenKind.PERIOD)
                return IfStmt(line=t.line, condition=condition,
                              then_body=then_body, else_body=else_body)
            else_body.append(self._parse_statement())
        raise ParseError("Unterminated 'if' block – missing 'end.'", t.line, t.col)

    # -- repeat <expr> times <stmts> end. -----------------------------------

    def _parse_repeat(self) -> RepeatStmt:
        t = self._advance()  # consume "repeat"
        saved_stops = self._stop_words
        self._stop_words = self._stop_words | frozenset({"times"})
        count = self._parse_expr()
        self._stop_words = saved_stops
        self._expect_word("times")
        body: List[Stmt] = []
        while not self._at_end():
            if self._check_word("end"):
                self._advance()
                self._expect_kind(TokenKind.PERIOD)
                return RepeatStmt(line=t.line, count=count, body=body)
            body.append(self._parse_statement())
        raise ParseError("Unterminated 'repeat' block – missing 'end.'", t.line, t.col)

    # -- while <expr> do <stmts> end. ---------------------------------------

    def _parse_while(self) -> WhileStmt:
        t = self._advance()  # consume "while"
        condition = self._parse_expr()
        self._expect_word("do")
        body: List[Stmt] = []
        while not self._at_end():
            if self._check_word("end"):
                self._advance()
                self._expect_kind(TokenKind.PERIOD)
                return WhileStmt(line=t.line, condition=condition, body=body)
            body.append(self._parse_statement())
        raise ParseError("Unterminated 'while' block – missing 'end.'", t.line, t.col)

    # -- for each <name> from <expr> to <expr> [by <expr>] do <stmts> end. -

    def _parse_for_each(self) -> ForEachStmt:
        t = self._advance()  # consume "for"
        self._expect_word("each")
        name_tok = self._advance()
        if name_tok.kind != TokenKind.WORD:
            raise ParseError(
                "Expected variable name after 'for each'",
                name_tok.line, name_tok.col,
            )
        self._expect_word("from")

        saved_stops = self._stop_words
        self._stop_words = saved_stops | frozenset({"to"})
        start_expr = self._parse_expr()
        self._stop_words = saved_stops

        self._expect_word("to")

        saved_stops = self._stop_words
        self._stop_words = saved_stops | frozenset({"by"})
        end_expr = self._parse_expr()
        self._stop_words = saved_stops

        step_expr: Optional[Expr] = None
        if self._check_word("by"):
            self._advance()
            step_expr = self._parse_expr()

        self._expect_word("do")
        body: List[Stmt] = []
        while not self._at_end():
            if self._check_word("end"):
                self._advance()
                self._expect_kind(TokenKind.PERIOD)
                return ForEachStmt(
                    line=t.line,
                    var_name=name_tok.value,
                    start=start_expr,
                    end=end_expr,
                    step=step_expr,
                    body=body,
                )
            body.append(self._parse_statement())
        raise ParseError("Unterminated 'for each' block – missing 'end.'", t.line, t.col)

    # -- stop. / skip. ------------------------------------------------------

    def _parse_stop(self) -> StopStmt:
        t = self._advance()  # consume "stop"
        self._expect_kind(TokenKind.PERIOD)
        return StopStmt(line=t.line)

    def _parse_skip(self) -> SkipStmt:
        t = self._advance()  # consume "skip"
        self._expect_kind(TokenKind.PERIOD)
        return SkipStmt(line=t.line)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(tokens: List[Token]) -> List[Stmt]:
    """Parse a list of tokens into a list of statement AST nodes."""
    p = _Parser(tokens)
    return p.parse_program()
