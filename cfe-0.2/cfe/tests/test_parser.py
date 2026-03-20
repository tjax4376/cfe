"""Tests for the CFD v2 parser."""

import unittest
from cfe.lexer import lex
from cfe.parser import (
    parse, ParseError,
    SetStmt, SayStmt, AskStmt, IfStmt, RepeatStmt,
    WhileStmt, ForEachStmt, StopStmt, SkipStmt,
    NumberLiteral, DecimalLiteral, TextLiteral, BoolLiteral,
    NoneLiteral, VarRef, BinaryExpr, UnaryExpr, LengthExpr,
)


def _parse(source: str):
    return parse(lex(source))


class TestParseAtoms(unittest.TestCase):

    def test_number(self):
        stmts = _parse("set x to 5.")
        self.assertIsInstance(stmts[0], SetStmt)
        self.assertIsInstance(stmts[0].value, NumberLiteral)
        self.assertEqual(stmts[0].value.value, 5)

    def test_decimal(self):
        stmts = _parse("set x to 3 point 14.")
        self.assertIsInstance(stmts[0].value, DecimalLiteral)
        self.assertAlmostEqual(stmts[0].value.value, 3.14)

    def test_text_literal(self):
        stmts = _parse("set x to text, hello world.")
        self.assertIsInstance(stmts[0].value, TextLiteral)
        self.assertEqual(stmts[0].value.value, "hello world")

    def test_bool_true(self):
        stmts = _parse("set x to true.")
        self.assertIsInstance(stmts[0].value, BoolLiteral)
        self.assertTrue(stmts[0].value.value)

    def test_bool_false(self):
        stmts = _parse("set x to false.")
        self.assertIsInstance(stmts[0].value, BoolLiteral)
        self.assertFalse(stmts[0].value.value)

    def test_none(self):
        stmts = _parse("set x to none.")
        self.assertIsInstance(stmts[0].value, NoneLiteral)

    def test_varref(self):
        stmts = _parse("set x to y.")
        self.assertIsInstance(stmts[0].value, VarRef)
        self.assertEqual(stmts[0].value.name, "y")


class TestParseArithmetic(unittest.TestCase):

    def test_plus(self):
        stmts = _parse("set x to 1 plus 2.")
        expr = stmts[0].value
        self.assertIsInstance(expr, BinaryExpr)
        self.assertEqual(expr.op, "plus")

    def test_times(self):
        stmts = _parse("set x to 3 times 4.")
        self.assertEqual(stmts[0].value.op, "times")

    def test_divided_by(self):
        stmts = _parse("set x to 10 divided by 2.")
        self.assertEqual(stmts[0].value.op, "divided by")

    def test_modulo(self):
        stmts = _parse("set x to 10 modulo 3.")
        self.assertEqual(stmts[0].value.op, "modulo")

    def test_negative(self):
        stmts = _parse("set x to negative 5.")
        expr = stmts[0].value
        self.assertIsInstance(expr, UnaryExpr)
        self.assertEqual(expr.op, "negative")

    def test_precedence_times_over_plus(self):
        stmts = _parse("set x to 1 plus 2 times 3.")
        expr = stmts[0].value
        self.assertEqual(expr.op, "plus")
        self.assertIsInstance(expr.right, BinaryExpr)
        self.assertEqual(expr.right.op, "times")


class TestParseComparisons(unittest.TestCase):

    def test_is(self):
        stmts = _parse("if x is 5 then say x. end.")
        self.assertIsInstance(stmts[0].condition, BinaryExpr)
        self.assertEqual(stmts[0].condition.op, "is")

    def test_is_not(self):
        stmts = _parse("if x is not 5 then say x. end.")
        self.assertEqual(stmts[0].condition.op, "is not")

    def test_greater_than(self):
        stmts = _parse("if x is greater than 5 then say x. end.")
        self.assertEqual(stmts[0].condition.op, "is greater than")

    def test_less_than(self):
        stmts = _parse("if x is less than 5 then say x. end.")
        self.assertEqual(stmts[0].condition.op, "is less than")

    def test_at_least(self):
        stmts = _parse("if x is at least 5 then say x. end.")
        self.assertEqual(stmts[0].condition.op, "is at least")

    def test_at_most(self):
        stmts = _parse("if x is at most 5 then say x. end.")
        self.assertEqual(stmts[0].condition.op, "is at most")


class TestParseLogic(unittest.TestCase):

    def test_and(self):
        stmts = _parse("if x is 1 and y is 2 then say x. end.")
        cond = stmts[0].condition
        self.assertEqual(cond.op, "and")

    def test_or(self):
        stmts = _parse("if x is 1 or y is 2 then say x. end.")
        self.assertEqual(stmts[0].condition.op, "or")

    def test_not(self):
        stmts = _parse("if not x is 1 then say x. end.")
        cond = stmts[0].condition
        self.assertIsInstance(cond, UnaryExpr)
        self.assertEqual(cond.op, "not")


class TestParseStatements(unittest.TestCase):

    def test_say_multiple(self):
        stmts = _parse("say 1, 2, 3.")
        self.assertEqual(len(stmts[0].values), 3)

    def test_ask(self):
        stmts = _parse("ask name.")
        self.assertIsInstance(stmts[0], AskStmt)
        self.assertEqual(stmts[0].name, "name")

    def test_if_else(self):
        stmts = _parse("if x is 1 then say x. else say y. end.")
        self.assertEqual(len(stmts[0].then_body), 1)
        self.assertEqual(len(stmts[0].else_body), 1)

    def test_repeat(self):
        stmts = _parse("repeat 3 times say hello. end.")
        self.assertIsInstance(stmts[0], RepeatStmt)
        self.assertEqual(len(stmts[0].body), 1)

    def test_repeat_with_var(self):
        stmts = _parse("repeat n times say hello. end.")
        self.assertIsInstance(stmts[0].count, VarRef)

    def test_length(self):
        stmts = _parse("set x to the length of y.")
        self.assertIsInstance(stmts[0].value, LengthExpr)

    def test_joined_with(self):
        stmts = _parse("set x to a joined with b.")
        self.assertEqual(stmts[0].value.op, "joined with")


class TestParsePhase2(unittest.TestCase):

    def test_while(self):
        stmts = _parse("while x is less than 10 do say x. end.")
        self.assertIsInstance(stmts[0], WhileStmt)
        self.assertIsInstance(stmts[0].condition, BinaryExpr)
        self.assertEqual(stmts[0].condition.op, "is less than")
        self.assertEqual(len(stmts[0].body), 1)

    def test_while_multiple_body(self):
        stmts = _parse("while true do say 1. say 2. end.")
        self.assertIsInstance(stmts[0], WhileStmt)
        self.assertEqual(len(stmts[0].body), 2)

    def test_for_each_basic(self):
        stmts = _parse("for each i from 1 to 5 do say i. end.")
        self.assertIsInstance(stmts[0], ForEachStmt)
        self.assertEqual(stmts[0].var_name, "i")
        self.assertIsInstance(stmts[0].start, NumberLiteral)
        self.assertEqual(stmts[0].start.value, 1)
        self.assertIsInstance(stmts[0].end, NumberLiteral)
        self.assertEqual(stmts[0].end.value, 5)
        self.assertIsNone(stmts[0].step)
        self.assertEqual(len(stmts[0].body), 1)

    def test_for_each_with_step(self):
        stmts = _parse("for each i from 0 to 10 by 2 do say i. end.")
        self.assertIsInstance(stmts[0], ForEachStmt)
        self.assertIsNotNone(stmts[0].step)
        self.assertIsInstance(stmts[0].step, NumberLiteral)
        self.assertEqual(stmts[0].step.value, 2)

    def test_for_each_negative_step(self):
        stmts = _parse("for each i from 5 to 1 by negative 1 do say i. end.")
        self.assertIsInstance(stmts[0].step, UnaryExpr)
        self.assertEqual(stmts[0].step.op, "negative")

    def test_for_each_expr_range(self):
        stmts = _parse("for each i from 1 plus 1 to 3 times 3 do say i. end.")
        self.assertIsInstance(stmts[0].start, BinaryExpr)
        self.assertEqual(stmts[0].start.op, "plus")
        self.assertIsInstance(stmts[0].end, BinaryExpr)
        self.assertEqual(stmts[0].end.op, "times")

    def test_for_each_with_var_range(self):
        stmts = _parse("for each i from start to finish do say i. end.")
        self.assertIsInstance(stmts[0].start, VarRef)
        self.assertEqual(stmts[0].start.name, "start")
        self.assertIsInstance(stmts[0].end, VarRef)
        self.assertEqual(stmts[0].end.name, "finish")

    def test_stop(self):
        stmts = _parse("stop.")
        self.assertIsInstance(stmts[0], StopStmt)

    def test_skip(self):
        stmts = _parse("skip.")
        self.assertIsInstance(stmts[0], SkipStmt)

    def test_stop_inside_repeat(self):
        stmts = _parse("repeat 10 times if x is 5 then stop. end. end.")
        body = stmts[0].body
        self.assertIsInstance(body[0], IfStmt)
        self.assertIsInstance(body[0].then_body[0], StopStmt)

    def test_skip_inside_while(self):
        stmts = _parse("while true do if x is 3 then skip. end. say x. end.")
        body = stmts[0].body
        self.assertIsInstance(body[0], IfStmt)
        self.assertIsInstance(body[0].then_body[0], SkipStmt)

    def test_for_each_divided_by_in_end_expr(self):
        stmts = _parse("for each i from 1 to 10 divided by 2 do say i. end.")
        self.assertIsInstance(stmts[0].end, BinaryExpr)
        self.assertEqual(stmts[0].end.op, "divided by")


class TestParseErrors(unittest.TestCase):

    def test_unknown_keyword(self):
        with self.assertRaises(ParseError):
            _parse("frobnicate x.")

    def test_unterminated_if(self):
        with self.assertRaises(ParseError):
            _parse("if x is 1 then say x.")

    def test_unterminated_while(self):
        with self.assertRaises(ParseError):
            _parse("while true do say x.")

    def test_unterminated_for_each(self):
        with self.assertRaises(ParseError):
            _parse("for each i from 1 to 5 do say i.")


if __name__ == "__main__":
    unittest.main()
