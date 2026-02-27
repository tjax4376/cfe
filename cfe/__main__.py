"""
CFE CLI entrypoint – run with ``python3 -m cfe <file.cfd>``.

Version: 2.1
Author: Generated for aidev
Change rationale: Provide a CFE module entrypoint that forwards to the
existing CFD CLI while the implementation is migrated.
"""

from __future__ import annotations

from cfd.__main__ import main


if __name__ == "__main__":
    main()

