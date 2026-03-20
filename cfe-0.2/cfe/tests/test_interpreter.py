"""Tests for the CFD v2 interpreter."""

import io
import sys
import unittest

from cfe.lexer import lex
from cfe.parser import parse
from cfe.interpreter import run, execute, CfeRuntimeError


def _run(source: str) -> str:
    """Run a CFD program and capture stdout."""
    tokens = lex(source)
    ast = parse(tokens)
    buf = io.StringIO()
    old_out = sys.stdout
    sys.stdout = buf
    try:
        execute(ast)
    finally:
        sys.stdout = old_out
    return buf.getvalue()


class TestArithmetic(unittest.TestCase):

    def test_plus(self):
        out = _run("set x to 2 plus 3. say x.")
        self.assertEqual(out.strip(), "5")

    def test_minus(self):
        out = _run("set x to 10 minus 4. say x.")
        self.assertEqual(out.strip(), "6")

    def test_times(self):
        out = _run("set x to 3 times 4. say x.")
        self.assertEqual(out.strip(), "12")

    def test_divided_by(self):
        out = _run("set x to 10 divided by 3. say x.")
        self.assertEqual(out.strip(), "3")

    def test_modulo(self):
        out = _run("set x to 10 modulo 3. say x.")
        self.assertEqual(out.strip(), "1")

    def test_negative(self):
        out = _run("set x to negative 7. say x.")
        self.assertEqual(out.strip(), "-7")

    def test_decimal(self):
        out = _run("set x to 3 point 14. say x.")
        self.assertEqual(out.strip(), "3.14")

    def test_mixed_decimal(self):
        out = _run("set x to 1 plus 0 point 5. say x.")
        self.assertEqual(out.strip(), "1.5")

    def test_precedence(self):
        out = _run("set x to 2 plus 3 times 4. say x.")
        self.assertEqual(out.strip(), "14")

    def test_division_by_zero(self):
        with self.assertRaises(CfeRuntimeError):
            _run("set x to 1 divided by 0.")


class TestComparisons(unittest.TestCase):

    def test_is(self):
        out = _run("if 5 is 5 then say text, yes. end.")
        self.assertEqual(out.strip(), "yes")

    def test_is_not(self):
        out = _run("if 5 is not 3 then say text, yes. end.")
        self.assertEqual(out.strip(), "yes")

    def test_greater_than(self):
        out = _run("if 10 is greater than 5 then say text, yes. end.")
        self.assertEqual(out.strip(), "yes")

    def test_less_than(self):
        out = _run("if 3 is less than 5 then say text, yes. end.")
        self.assertEqual(out.strip(), "yes")

    def test_at_least(self):
        out = _run("if 5 is at least 5 then say text, yes. end.")
        self.assertEqual(out.strip(), "yes")

    def test_at_most(self):
        out = _run("if 5 is at most 5 then say text, yes. end.")
        self.assertEqual(out.strip(), "yes")


class TestLogic(unittest.TestCase):

    def test_and_true(self):
        out = _run("if 1 is 1 and 2 is 2 then say text, yes. end.")
        self.assertEqual(out.strip(), "yes")

    def test_and_false(self):
        out = _run("if 1 is 1 and 2 is 3 then say text, yes. else say text, no. end.")
        self.assertEqual(out.strip(), "no")

    def test_or_true(self):
        out = _run("if 1 is 2 or 2 is 2 then say text, yes. end.")
        self.assertEqual(out.strip(), "yes")

    def test_not(self):
        out = _run("if not 1 is 2 then say text, yes. end.")
        self.assertEqual(out.strip(), "yes")


class TestText(unittest.TestCase):

    def test_text_literal(self):
        out = _run("say text, hello world.")
        self.assertEqual(out.strip(), "hello world")

    def test_joined_with(self):
        out = _run("set a to text, hello. set b to text, world. set c to a joined with b. say c.")
        self.assertEqual(out.strip(), "helloworld")

    def test_length(self):
        out = _run("set x to text, hello. set n to the length of x. say n.")
        self.assertEqual(out.strip(), "5")


class TestTypes(unittest.TestCase):

    def test_boolean_true(self):
        out = _run("set x to true. if x then say text, yes. end.")
        self.assertEqual(out.strip(), "yes")

    def test_boolean_false(self):
        out = _run("set x to false. if x then say text, yes. else say text, no. end.")
        self.assertEqual(out.strip(), "no")

    def test_none(self):
        out = _run("set x to none. say x.")
        self.assertEqual(out.strip(), "none")


class TestControlFlow(unittest.TestCase):

    def test_if_then(self):
        out = _run("if 1 is 1 then say text, yes. end.")
        self.assertEqual(out.strip(), "yes")

    def test_if_else(self):
        out = _run("if 1 is 2 then say text, yes. else say text, no. end.")
        self.assertEqual(out.strip(), "no")

    def test_repeat(self):
        out = _run("set c to 0. repeat 3 times set c to c plus 1. end. say c.")
        self.assertEqual(out.strip(), "3")

    def test_repeat_variable(self):
        out = _run("set n to 2. repeat n times say text, hi. end.")
        self.assertEqual(out.strip(), "hi\nhi")

    def test_nested_repeat(self):
        out = _run("set c to 0. repeat 2 times repeat 3 times set c to c plus 1. end. end. say c.")
        self.assertEqual(out.strip(), "6")


class TestSay(unittest.TestCase):

    def test_say_multiple(self):
        out = _run("say 1, 2, 3.")
        self.assertEqual(out.strip(), "1 2 3")

    def test_say_mixed(self):
        out = _run("set x to 5. say text, value is, x.")
        self.assertEqual(out.strip(), "value is 5")


# =========================================================================
# Phase 2 tests
# =========================================================================

class TestWhile(unittest.TestCase):

    def test_while_basic(self):
        out = _run(
            "set x to 0. "
            "while x is less than 3 do "
            "  set x to x plus 1. "
            "end. "
            "say x."
        )
        self.assertEqual(out.strip(), "3")

    def test_while_prints(self):
        out = _run(
            "set x to 1. "
            "while x is at most 3 do "
            "  say x. "
            "  set x to x plus 1. "
            "end."
        )
        self.assertEqual(out.strip(), "1\n2\n3")

    def test_while_false_condition(self):
        out = _run("while false do say text, never. end.")
        self.assertEqual(out.strip(), "")

    def test_while_complex_condition(self):
        out = _run(
            "set x to 0. "
            "while x is less than 10 and x is not 5 do "
            "  set x to x plus 1. "
            "end. "
            "say x."
        )
        self.assertEqual(out.strip(), "5")


class TestForEach(unittest.TestCase):

    def test_for_each_basic(self):
        out = _run(
            "for each i from 1 to 5 do "
            "  say i. "
            "end."
        )
        self.assertEqual(out.strip(), "1\n2\n3\n4\n5")

    def test_for_each_with_step(self):
        out = _run(
            "for each i from 0 to 10 by 3 do "
            "  say i. "
            "end."
        )
        self.assertEqual(out.strip(), "0\n3\n6\n9")

    def test_for_each_countdown(self):
        out = _run(
            "for each i from 5 to 1 by negative 1 do "
            "  say i. "
            "end."
        )
        self.assertEqual(out.strip(), "5\n4\n3\n2\n1")

    def test_for_each_no_iterations(self):
        out = _run("for each i from 10 to 1 do say i. end.")
        self.assertEqual(out.strip(), "")

    def test_for_each_decimal_step(self):
        out = _run(
            "for each x from 0 to 1 by 0 point 5 do "
            "  say x. "
            "end."
        )
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], "0")
        self.assertEqual(lines[1], "0.5")
        self.assertEqual(lines[2], "1")

    def test_for_each_expr_bounds(self):
        out = _run(
            "set a to 2. set b to 4. "
            "for each i from a to a plus b do "
            "  say i. "
            "end."
        )
        self.assertEqual(out.strip(), "2\n3\n4\n5\n6")

    def test_for_each_accumulator(self):
        out = _run(
            "set total to 0. "
            "for each i from 1 to 5 do "
            "  set total to total plus i. "
            "end. "
            "say total."
        )
        self.assertEqual(out.strip(), "15")

    def test_for_each_zero_step_error(self):
        with self.assertRaises(CfeRuntimeError):
            _run("for each i from 1 to 10 by 0 do say i. end.")

    def test_for_each_divided_by_in_end(self):
        out = _run(
            "for each i from 1 to 10 divided by 2 do "
            "  say i. "
            "end."
        )
        self.assertEqual(out.strip(), "1\n2\n3\n4\n5")


class TestStopSkip(unittest.TestCase):

    def test_stop_in_repeat(self):
        out = _run(
            "set i to 0. "
            "repeat 10 times "
            "  set i to i plus 1. "
            "  if i is 3 then stop. end. "
            "  say i. "
            "end."
        )
        self.assertEqual(out.strip(), "1\n2")

    def test_stop_in_while(self):
        out = _run(
            "set i to 0. "
            "while true do "
            "  set i to i plus 1. "
            "  if i is 4 then stop. end. "
            "end. "
            "say i."
        )
        self.assertEqual(out.strip(), "4")

    def test_stop_in_for_each(self):
        out = _run(
            "for each i from 1 to 100 do "
            "  if i is 4 then stop. end. "
            "  say i. "
            "end."
        )
        self.assertEqual(out.strip(), "1\n2\n3")

    def test_skip_in_repeat(self):
        out = _run(
            "set i to 0. "
            "repeat 5 times "
            "  set i to i plus 1. "
            "  if i is 3 then skip. end. "
            "  say i. "
            "end."
        )
        self.assertEqual(out.strip(), "1\n2\n4\n5")

    def test_skip_in_while(self):
        out = _run(
            "set i to 0. "
            "while i is less than 5 do "
            "  set i to i plus 1. "
            "  if i is 3 then skip. end. "
            "  say i. "
            "end."
        )
        self.assertEqual(out.strip(), "1\n2\n4\n5")

    def test_skip_in_for_each(self):
        out = _run(
            "for each i from 1 to 5 do "
            "  if i is 3 then skip. end. "
            "  say i. "
            "end."
        )
        self.assertEqual(out.strip(), "1\n2\n4\n5")

    def test_stop_breaks_inner_loop_only(self):
        out = _run(
            "repeat 3 times "
            "  for each i from 1 to 100 do "
            "    if i is 2 then stop. end. "
            "    say i. "
            "  end. "
            "end."
        )
        self.assertEqual(out.strip(), "1\n1\n1")

    def test_stop_outside_loop(self):
        with self.assertRaises(CfeRuntimeError):
            _run("stop.")

    def test_skip_outside_loop(self):
        with self.assertRaises(CfeRuntimeError):
            _run("skip.")


if __name__ == "__main__":
    unittest.main()
