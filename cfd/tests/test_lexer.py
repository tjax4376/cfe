"""Tests for the CFD v2 lexer."""

import unittest
from cfd.lexer import TokenKind, lex, LexError


class TestLex(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(lex(""), [])

    def test_whitespace_only(self):
        self.assertEqual(lex("   \n\t\r  "), [])

    def test_single_word(self):
        tokens = lex("hello")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].kind, TokenKind.WORD)
        self.assertEqual(tokens[0].value, "hello")

    def test_number(self):
        tokens = lex("42")
        self.assertEqual(tokens[0].value, "42")

    def test_period(self):
        tokens = lex("say hello.")
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[2].kind, TokenKind.PERIOD)

    def test_comma(self):
        tokens = lex("a, b")
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[1].kind, TokenKind.COMMA)

    def test_mixed_statement(self):
        tokens = lex("set x to 5.")
        kinds = [t.kind for t in tokens]
        self.assertEqual(kinds, [
            TokenKind.WORD, TokenKind.WORD, TokenKind.WORD,
            TokenKind.WORD, TokenKind.PERIOD,
        ])

    def test_newline_tracking(self):
        tokens = lex("a\nb")
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[1].line, 2)

    def test_alphanumeric_split(self):
        tokens = lex("v2")
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].value, "v")
        self.assertEqual(tokens[1].value, "2")


if __name__ == "__main__":
    unittest.main()
