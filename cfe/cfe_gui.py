"""
CFE GUI shim – forwards to the CFD tkinter GUI runtime.

Version: 0.2
Author: Generated for aidev
Change rationale: Provide ``cfe.cfe_gui`` so future GUI integration can use the
new CFE name while reusing the existing ``cfd.cfd_gui`` implementation.
"""

from __future__ import annotations

from cfd.cfd_gui import *  # noqa: F401,F403

