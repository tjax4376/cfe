"""
CFE parser shim – forwards to the CFD v2 parser.

Version: 2.1
Author: Generated for aidev
Change rationale: Provide ``cfe.parser`` as an alias so code can import the
language under its new name while the implementation remains in ``cfd.parser``.
"""

from __future__ import annotations

from cfd.parser import *  # noqa: F401,F403

