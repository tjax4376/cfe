"""
CFE CLI entrypoint – run with ``python3 -m cfe <file.cfe>``.

Version: 0.2
Author: Generated for aidev
Change rationale: Local implementation; lex → parse → execute using cfe modules.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .lexer import LexError, lex
from .parser import ParseError, parse
from .interpreter import CfeRuntimeError, execute


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 -m cfe <file.cfe>", file=sys.stderr)
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
    except CfeRuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
