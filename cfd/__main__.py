"""
CFD CLI entrypoint – run with ``python3 -m cfd <file.cfd>``.

Version: 2.1
Author: Generated for aidev
Change rationale: Phase 2 – use execute() to catch stray loop signals.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .lexer import LexError, lex
from .parser import ParseError, parse
from .interpreter import CfdRuntimeError, execute


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 -m cfd <file.cfd>", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    source = path.read_text()
    try:
        tokens = lex(source)
        ast = parse(tokens)
        execute(ast)
    except LexError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except ParseError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except CfdRuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
