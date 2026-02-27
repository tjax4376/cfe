# Plan: Rename CFD to CFE (Coding For Everyone)

**Status:** Design only (no implementation yet).  
**Scope:** Introduce a `cfe` identity (package, CLI, docs) while keeping a thin
`cfd` shim for compatibility, then retire `cfd` after a transition period.

---

## 1. Goals and rename strategy

- Change the primary language branding from **CFD (Code for Dummies)** to
  **CFE (Coding For Everyone)**.
- Provide:
  - A `cfe` Python package and `python3 -m cfe` entrypoint.
  - A `cfe` standalone executable via PyInstaller.
  - Updated docs/spec using the new name.
- Keep the codebase buildable at each step and avoid breaking existing scripts
  abruptly by using a **thin `cfd` shim** that forwards to `cfe`.

High-level steps:

1. Introduce `cfe` package and CLI entrypoint.
2. Move core implementation modules from `cfd` to `cfe`.
3. Turn `cfd` into a small compatibility layer.
4. Update docs, examples, and build scripts to prefer `cfe`.
5. Plan eventual removal of the shim once consumers have migrated.

---

## 2. Step-by-step path

### 2.1 Add `cfe` package and CLI

- Create a new `cfe` package directory mirroring the current `cfd` public
  surface:

  ```text
  cfe/
    __init__.py
    __main__.py
  ```

- For the first iteration, `cfe.__main__.py` can import and forward to the
  existing `cfd` implementation:

  ```python
  from cfd.__main__ import main  # temporary forwarding
  ```

- Ensure `python3 -m cfe examples/showcase.cfd` runs the same programs as
  `python3 -m cfd` initially.

### 2.2 Move implementation modules into `cfe`

- Create full `cfe` equivalents of the core modules:

  ```text
  cfe/
    lexer.py
    parser.py
    typesystem.py
    interpreter.py
    cfe_gui.py
    __main__.py
    __init__.py
  ```

- Move or copy code from `cfd/*.py` into `cfe/*.py`, updating internal imports
  to use `from .lexer import ...` etc.
- Verify tests can run entirely against `cfe`:
  - Option A: keep tests importing `cfd` but let `cfd` forward to `cfe`.
  - Option B: update tests to import `cfe` directly once the move is complete.

### 2.3 Turn `cfd` into a shim

- Replace `cfd` implementation modules with thin wrappers that import from
  `cfe`:

  ```python
  # cfd/interpreter.py (shim)
  from cfe.interpreter import *  # or explicit re-exports
  ```

- Keep `cfd/__main__.py` and `cfd/cfd.py` forwarding to `cfe`:
  - `cfd.__main__` can import and call `cfe.__main__.main`.
  - `cfd/cfd.py` remains a CLI wrapper but now targets `cfe`.
- Add clear comments and, if appropriate, runtime warnings indicating that the
  `cfd` namespace is deprecated and that `cfe` is the preferred entrypoint.

### 2.4 Update docs, examples, and build scripts

- Rename references in:
  - `README.md` – introduce CFE name, note that CFD is the old name.
  - `SPEC.md` – describe the language as CFE/CFD, with CFE as the canonical
    label going forward.
  - `journal` entries – record rename steps and rationale.
- Update examples:
  - Keep existing `.cfd` examples for backward compatibility.
  - Optionally add `.cfe` copies of key examples to demonstrate the new
    extension while the interpreter still accepts both.
- Update `build_standalone.sh` and `cfd.spec`:
  - Primary executable name becomes `cfe` (with `cfd` as an optional alias).
  - Eventually add a `cfe.spec` if needed for clarity.

### 2.5 Plan for eventual removal of `cfd`

- Document a deprecation timeline (even if informal for now) in `README.md`:
  - Short term: `cfd` and `cfe` both work; `cfe` is recommended.
  - Medium term: `cfd` remains a thin shim, may log a deprecation warning.
  - Long term: remove `cfd` once consumers have migrated (manual decision).
- Keep the shim extremely small and well-tested so that it does not accrue
  independent behaviour.

---

## 3. CI/CD and testing considerations

- Ensure the test suite continues to run green after each step:
  - First against `cfd` (current behaviour).
  - Then against both `cfd` and `cfe` (during the transition).
  - Finally against `cfe` only once the shim is stable.
- For PyInstaller builds:
  - Add or update specs to build a `cfe` binary.
  - Optionally keep a `cfd` binary as a symlink or small wrapper that forwards
    to `cfe`.

---

## 4. Security and robustness notes

- The rename itself does not change language semantics, but:
  - All new code added during the move (e.g. shims) must not suppress errors.
  - Any warnings about deprecation should be explicit and non-fatal.
- Avoid duplication that could drift:
  - Prefer a single source of truth (`cfe`), with `cfd` simply importing and
    forwarding.

