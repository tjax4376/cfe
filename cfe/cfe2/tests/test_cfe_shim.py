"""Tests for the CFE shim – ensure cfe.* forwards to cfd.* correctly."""

from __future__ import annotations

import io
import sys
import unittest

from cfe.lexer import lex
from cfe.parser import parse
from cfe.interpreter import execute


class TestCfeShim(unittest.TestCase):
    def test_basic_hello(self) -> None:
        source = "say text, hello."
        tokens = lex(source)
        ast = parse(tokens)
        buf = io.StringIO()
        old_out = sys.stdout
        sys.stdout = buf
        try:
            execute(ast)
        finally:
            sys.stdout = old_out
        self.assertEqual(buf.getvalue().strip(), "hello")


if __name__ == "__main__":
    unittest.main()

