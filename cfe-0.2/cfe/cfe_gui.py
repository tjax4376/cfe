#!/usr/bin/env python3
"""
CFE GUI runtime (tkinter).

Version: 0.2
Change rationale: Windows and app support – create named windows, parent/child, labels, close button.

- Lazy import of tkinter so CLI-only scripts do not require a display.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

# Lazy: tkinter imported on first use to allow headless CLI runs.
_tk: Any = None


def _ensure_tk() -> Any:
    global _tk
    if _tk is None:
        import tkinter as _tk  # noqa: PLC0415
    return _tk


# State: root (first window), named windows, current window for add label/button.
_root: Optional[Any] = None
_windows: Dict[str, Any] = {}
_current: Optional[Any] = None
_content_frames: Dict[str, Any] = {}  # window name -> frame for packing widgets


def init() -> None:
    """Reset GUI state for a new run."""
    global _root, _windows, _current, _content_frames
    _root = None
    _windows = {}
    _current = None
    _content_frames = {}


def create_window(name: str, title: str, parent_name: Optional[str] = None) -> None:
    """Create a window (Tk or Toplevel). Becomes current window for add label / add close button."""
    global _root, _windows, _current, _content_frames
    tk = _ensure_tk()
    if parent_name is not None:
        if parent_name not in _windows:
            raise RuntimeError(f"Parent window {parent_name!r} does not exist.")
        parent = _windows[parent_name]
        win = tk.Toplevel(parent)
    else:
        if _root is not None:
            raise RuntimeError("Only one root window allowed. Use child of <name> for more windows.")
        win = tk.Tk()
        _root = win
    win.title(title)
    # Content frame so we can pack labels and close button vertically.
    frame = tk.Frame(win, padx=10, pady=10)
    frame.pack(fill=tk.BOTH, expand=True)
    _windows[name] = win
    _content_frames[name] = frame
    _current = frame


def add_label(text: str) -> None:
    """Add a label to the current window."""
    if _current is None:
        raise RuntimeError("No current window. Create a window first.")
    tk = _ensure_tk()
    lbl = tk.Label(_current, text=text)
    lbl.pack(anchor=tk.W)


def add_close_button() -> None:
    """Add a Close button that closes the current window (and its frame's master)."""
    if _current is None:
        raise RuntimeError("No current window. Create a window first.")
    tk = _ensure_tk()
    win = _current.winfo_toplevel()

    def on_close() -> None:
        win.destroy()

    btn = tk.Button(_current, text="Close", command=on_close)
    btn.pack(pady=(10, 0))


def show_windows() -> None:
    """Run the GUI event loop. Blocks until all windows are closed."""
    if _root is None:
        raise RuntimeError("No windows created. Create a window and then show windows.")
    _root.mainloop()
