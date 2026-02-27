#!/usr/bin/env python3
"""
CFD backward-compatibility wrapper.

Version: 2.0
Author: Generated for aidev
Change rationale: Phase 1 – thin shim so ``python3 cfd/cfd.py script.cfd``
                  still works.  Real logic lives in the package sub-modules.
"""

from __future__ import annotations

import os
import sys

# When executed directly (``python3 cfd/cfd.py``), the package is not on
# sys.path.  Add the parent directory so that ``from cfd.lexer import ...``
# resolves correctly.
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from cfd.__main__ import main  # noqa: E402

if __name__ == "__main__":
    main()
