"""
CFE interpreter shim – forwards to the CFD v2 interpreter.

Version: 2.1
Author: Generated for aidev
Change rationale: Provide ``cfe.interpreter`` as an alias so code can import
and execute programs under the new CFE name while the implementation remains
in ``cfd.interpreter``.
"""

from __future__ import annotations

from cfe.interpreter import *  # noqa: F401,F403

