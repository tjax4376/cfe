"""
CFE lexer shim – forwards to the CFD v2 lexer.

Version: 2.0
Author: Generated for aidev
Change rationale: Provide ``cfe.lexer`` as an alias so code can import the
language under its new name while the implementation remains in ``cfd.lexer``.
"""

from __future__ import annotations

from cfd.lexer import *  # noqa: F401,F403

