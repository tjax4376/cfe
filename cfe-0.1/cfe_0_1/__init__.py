"""
CFE 0.1 – compatibility layer; re-exports the CFE implementation.

Version: 0.1.0
Author: Generated for aidev
Change rationale: Legacy label for ex-CFD; forwards to cfe (cfe-0.2) so
                  scripts can depend on cfe_0_1 and get the same behaviour.
"""

from __future__ import annotations

try:
    from cfe import __version__ as __version__
except ImportError as e:
    raise ImportError(
        "cfe_0_1 requires the cfe package (add cfe-0.2 to PYTHONPATH)."
    ) from e
