# Plan: Windows and Application Building in CFD

**Status:** Implemented (tkinter, multi-window, close button). Standalone executable added per user choice.  
**Scope:** Add language constructs and runtime support so CFD can create windows and run as a GUI application.

---

## 1. Goal

- CFD scripts can **create windows** (e.g. one main window with a title).
- CFD scripts can **build an application** (run a .cfd file that opens a window and responds to user actions).
- Keep the language simple: only period, comma, and spaces; natural-language style.

---

## 2. Proposed CFD syntax (natural language, period-terminated)

All new statements end with a period. Comma separates arguments where it fits.

| Intent | Example |
|--------|--------|
| Create a window | `create window with title hello.` |
| Add a label (text) | `add label with text welcome.` |
| Add a button | `add button with label click me.` |
| Show the window (run app) | `show window.` |
| Optional: button runs CFD when clicked | `when button click do say clicked. end.` (or similar) |

**Constraints:** No new punctuation. Keywords: create, window, with, title, add, label, text, button, show, when, click, do.

---

## 3. Architecture options (needs your choice)

| Option | Pros | Cons |
|--------|------|------|
| **A. tkinter** | In Python stdlib, no extra deps, works everywhere Python runs | Look is basic, limited styling |
| **B. PyQt/PySide** | Rich widgets, native look | New dependency, license (GPL/Commercial) for Qt |
| **C. Web (browser)** | Modern look, easy to style | Requires browser, more complex (server or export to HTML/JS) |

**Recommendation for “simplest”:** **Option A (tkinter)** so the interpreter stays single-module deployable and runs with only Python 3.

---

## 4. Implementation approach (high level)

- **No change to core lexer/parser contract:** existing tokens (word, period, comma) stay; new keywords become new statement forms.
- **New AST nodes:** e.g. `CreateWindowStmt`, `AddLabelStmt`, `AddButtonStmt`, `ShowWindowStmt`, and optionally `WhenButtonClickStmt`.
- **GUI runtime:** Separate module (e.g. `cfd_gui.py`) that:
  - Builds a tkinter (or other) window when it receives “create window” / “add label” / “add button” / “show window”.
  - Runs on the same process as the interpreter; `show window` starts the GUI event loop.
- **CLI vs GUI:**
  - If the script contains no window-related keywords, behavior stays **CLI-only** (current behavior).
  - If the script contains window-related keywords, the interpreter builds the UI then runs `show window` to start the app (event loop blocks until window is closed).
- **Deploy:** One entrypoint (`python3 cfd/cfd.py app.cfd`); optional flag later like `--gui` if we want to force GUI mode.

---

## 5. What “build an application” means here

- **Build:** Write a .cfd source file that uses the new statements (create window, add label/button, show window).
- **Application:** Running that .cfd file with the interpreter opens a window; the user sees the UI and can interact (e.g. click a button). No separate “build step” (no compiler to exe); the application is “run this .cfd file with the CFD interpreter.”

---

## 6. Clarification questions (please answer in chat)

1. **GUI toolkit:** Are you okay with **tkinter** (no extra install), or do you want **PyQt/PySide** or a **web-based** UI?
2. **Interactivity:** Do you need **button click → run CFD code** (e.g. “when button click do say clicked. end.”), or is it enough in v1 to just **show a window with labels and buttons** (no actions yet)?
3. **One window only?** Is one window per script enough for the first version, or do you need multiple windows (e.g. “create second window.”)?
4. **Deployment:** Is “run with Python: `python3 cfd/cfd.py myapp.cfd`” sufficient, or do you eventually want a way to produce a **standalone executable** (e.g. PyInstaller) from a .cfd file?  
   **→ User chose: standalone executable.**

---

## 7. Standalone executable (implemented)

- **Tool:** PyInstaller.
- **Build:** From `cfd/` run `pyinstaller cfd.spec`; or from repo root run `./cfd/build_standalone.sh`.
- **Output:** `cfd/dist/cfd` (Unix) or `cfd/dist/cfd.exe` (Windows). Same usage: `./dist/cfd myapp.cfd`.
- **Artifacts:** `cfd.spec`, `build_standalone.sh`; README updated with instructions.
