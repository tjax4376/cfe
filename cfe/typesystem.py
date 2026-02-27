"""
CFE type system shim – forwards to the CFD v2 runtime types.

Version: 2.0
Author: Generated for aidev
Change rationale: Provide ``cfe.typesystem`` as an alias while the underlying
implementation continues to live in ``cfd.typesystem``.
"""

from __future__ import annotations

from cfd.typesystem import *  # noqa: F401,F403

