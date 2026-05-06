# Plan: Review CFD and Transpose Core Functionality into CFE

**Status:** Implemented (2025-03-14).  
**Created:** 2025-03-14  
**Scope:** Audit the `cfd` folder, define core functionality, and transpose it into `cfe` so that CFE is the canonical implementation. Folder names: ex-cfd → `cfe-0.1`, ex-cfe → `cfe-0.2`; build cfe only; all CFD references replaced with CFE.

---

## 1. Goals

- **Review** everything that exists in the `cfd` folder (modules, tests, examples, specs, build).
- **Define** core language functionality that must live in CFE.
- **Transpose** that core from `cfd` into `cfe` so that:
  - CFE is self-contained (lexer, parser, typesystem, interpreter in `cfe`).
  - CFE continues to own the agent stack (`cfe/agent/`).
  - CFD can be reduced to a thin shim that imports from CFE (per `PLAN-rename-cfd-to-cfe.md`).
- **Preserve** buildability, testability, and single CI/CD deployability at each step.

---

## 2. Review: What Exists in the CFD Folder

### 2.1 Core implementation modules

| Module           | Purpose | Location   | Dependencies |
|-----------------|---------|------------|--------------|
| `lexer.py`      | Tokeniser (WORD, PERIOD, COMMA) | `cfd/lexer.py` | None |
| `parser.py`     | AST builder (precedence climbing, all stmts including agent) | `cfd/parser.py` | `cfd.lexer` |
| `typesystem.py` | Runtime types (CfdType, coercion, to_text, etc.) | `cfd/typesystem.py` | None |
| `interpreter.py`| Statement/expression execution, loop signals, agent delegation | `cfd/interpreter.py` | `cfd.parser`, `cfd.typesystem`, **`cfe.agent.gateway`** |
| `cfd_gui.py`    | Tkinter GUI (windows, labels, lazy import) | `cfd/cfd_gui.py` | tkinter (lazy) |

**Critical dependency:** `cfd/interpreter.py` already imports `cfe.agent.gateway`. So the runtime today is **cfd core + cfe agent**.

### 2.2 Entrypoints and compatibility

- `cfd/__main__.py` – CLI: lex → parse → execute.
- `cfd/cfd.py` – Backward-compat CLI wrapper.
- `cfd/__init__.py` – Package marker, `__version__`.

### 2.3 Tests (in cfd)

- `test_lexer.py` – Lexer behaviour.
- `test_parser.py` – Parser (core + agent stmts).
- `test_interpreter.py` – Interpreter (core + loop signals).
- `test_agent_parser.py` – Agent-related AST (DefineAgentStmt, TellStmt, HearStmt, OpenChatStmt, ResponseFieldExpr).
- `test_agent_interpreter.py` – Interpreter agent execution (with mock gateway).
- `test_agent_gateway.py` – Gateway (likely in cfd but tests `cfe.agent`).
- `test_cfe_shim.py` – CFE shim behaviour.

### 2.4 Examples and docs

- Examples: `hello.cfd`, `showcase.cfd`, `condition.cfd`, `loop.cfd`, `for_each.cfd`, `while_loop.cfd`, `math.cfd`, `logic.cfd`, `text_ops.cfd`, `types.cfd`, `comparisons.cfd`, `stop_skip.cfd`, `agent_chat.cfe`, `agent_multi.cfe`.
- Docs: `README.md`, `SPEC.md`, `PLAN-*.md` (functions, testing, windows, rename, etc.).
- Build: `cfd.spec` (PyInstaller), `build_standalone.sh`, `requirements-dev.txt`.

### 2.5 Current CFE state

- **Shims only:** `cfe/lexer.py`, `parser.py`, `typesystem.py`, `interpreter.py`, `cfe_gui.py` each do `from cfd.<module> import *`.
- **Own implementation:** `cfe/agent/` (gateway, config, message, session, adapters).
- **Entrypoint:** `cfe/__main__.py` forwards to `cfd.__main__.main`.
- **Version:** `cfe/__init__.py` re-exports `__version__` from `cfd`.

---

## 3. Core Functionality to Transpose

“Core” is defined as everything required to run a CFE script (excluding the agent stack, which already lives in CFE):

1. **Lexer** – Token stream from source (`lexer.py`).
2. **Parser** – AST from tokens, including all statement and expression forms (including agent grammar) (`parser.py`).
3. **Typesystem** – Runtime types and coercion (`typesystem.py`).
4. **Interpreter** – Execution of AST; agent statements call `cfe.agent.gateway` (`interpreter.py`).
5. **GUI** – Optional tkinter runtime (`cfd_gui.py` → `cfe_gui.py`).

Agent-related AST nodes (DefineAgentStmt, TellStmt, HearStmt, OpenChatStmt, ResponseFieldExpr) and their execution are part of the core interpreter; only the **implementation** of the gateway lives in `cfe/agent/`. So the transpose includes the full parser and interpreter (with agent support), not a subset.

---

## 4. Transpose Strategy

### 4.1 Principle

- **Single source of truth:** After transpose, CFE holds the implementation; CFD becomes a thin shim.
- **No shared services between core and modules:** Agent remains a separate package surface; interpreter calls gateway via Python API (already the case).
- **Modular and independently testable:** Each moved file keeps clear boundaries; tests can target `cfe` directly.
- **CI/CD:** All new/updated code must remain buildable and testable from a single pipeline.

### 4.2 Steps (high level)

1. **Copy implementation into CFE (no delete from CFD yet)**  
   - Copy `cfd/lexer.py` → `cfe/lexer.py` (full implementation).  
   - Copy `cfd/parser.py` → `cfe/parser.py`; update internal imports from `cfd.lexer` to `cfe.lexer` (and same for any `cfd` references).  
   - Copy `cfd/typesystem.py` → `cfe/typesystem.py`.  
   - Copy `cfd/interpreter.py` → `cfe/interpreter.py`; change imports from `cfd.parser` / `cfd.typesystem` to `cfe.parser` / `cfe.typesystem`; keep `from cfe.agent.gateway import Gateway` (already correct when code lives in cfe).  
   - Copy `cfd/cfd_gui.py` → `cfe/cfe_gui.py`; adjust any self-references if needed (e.g. docstrings).  

2. **Update CFE entrypoint**  
   - `cfe/__main__.py`: implement CLI locally (lex → parse → execute using `cfe.lexer`, `cfe.parser`, `cfe.interpreter`) instead of forwarding to `cfd.__main__.main`.  
   - `cfe/__init__.py`: keep or set `__version__` in CFE (no re-export from cfd).  

3. **Tests**  
   - Add or relocate tests so that:  
     - Core language tests run against `cfe` (lexer, parser, interpreter, agent parser, agent interpreter with mock gateway).  
   - Options:  
     - **A)** Move `cfd/tests/*` into `cfe/tests/` and change imports to `cfe.*`.  
     - **B)** Keep tests under `cfd/tests/` but have them import and run `cfe` instead of `cfd` for core behaviour.  
   - Recommendation: **A** for clarity (CFE is canonical; tests live with implementation).  

4. **Turn CFD into a shim**  
   - Replace `cfd/lexer.py`, `parser.py`, `typesystem.py`, `interpreter.py`, `cfd_gui.py` with thin wrappers that re-export from `cfe` (e.g. `from cfe.lexer import *`).  
   - `cfd/__main__.py`: forward to `cfe.__main__.main` (or call the same pipeline).  
   - Ensure `python3 -m cfd <file>` and `python3 -m cfe <file>` both work.  

5. **Docs and build**  
   - Update `README.md` (and any top-level docs) to state that CFE is the primary implementation and CFD is the compatibility layer.  
   - Update `cfd/README.md` / `SPEC.md` as needed.  
   - Build: ensure `cfe.spec` (or equivalent) produces the primary `cfe` executable; optionally keep `cfd` build as alias/shim.  

### 4.3 Order of operations (to avoid broken builds)

1. Implement CFE core modules (copy + fix imports).  
2. Run tests against CFE only (new or moved tests).  
3. Switch CFE `__main__` to use local implementation.  
4. Verify `python3 -m cfe <file>` and existing agent examples.  
5. Replace CFD implementation with shims; verify `python3 -m cfd <file>`.  
6. Update docs and build.  

---

## 5. Resolved decisions (implemented)

- **Interface Contract:** The interpreter in `cfe/interpreter.py` calls `gw.send(message: Message)` on the gateway instance obtained via a lazy-loaded singleton (`_get_gateway()`). The gateway must implement `send(message: Message) -> Response`. The interpreter constructs a `cfe.agent.message.Message` object, which contains either `text` or `payload`. The gateway returns a `cfe.agent.message.Response` object, which the interpreter stores in the environment under a specific key (`_last_response_{agent}`).

- **GUI Entrypoint:** `cfe/__main__.py` will be updated to use `argparse`. It will default to CLI execution (lex $\rightarrow$ parse $\rightarrow$ execute). If the `--gui` flag is present, it will delegate execution to `cfe/cfe_gui.py`.

- **Test Migration:** Tests from `cfd/tests/*` will be moved to `cfe/tests/*`. This migration is conditional: I will first run all existing tests against the current `cfd` structure. If any test fails, I will pause and require your review before proceeding with the move/rename to ensure no hidden dependencies are broken.

---

## 6. Security and Constraints (PHA / user rules)

- No hardcoded secrets; agent API keys remain in config/env.  
- No silent error suppression; all error handling must log or fail safely.  
- Critical paths (auth, agent gateway) remain human-reviewable.  
- Multi-module change: this plan spans cfd and cfe; each step must leave the repo buildable and tests green.  
- Core and modules stay integrated via clear APIs (interpreter → gateway), not shared services.  

---

## 7. Success Criteria

- CFE contains full lexer, parser, typesystem, interpreter, and GUI implementation.  
- CFE interpreter uses `cfe.agent.gateway`; no dependency on `cfd` for execution.  
- `python3 -m cfe <file>` runs all existing .cfd/.cfe examples.  
- CFD is a thin shim; `python3 -m cfd <file>` behaves identically.  
- All tests pass (whether under `cfe/tests` or `cfd/tests` with cfe imports).  
- Single CI/CD pipeline can build and test both packages.  
- `.memory/cards.md` and known limitations (e.g. text literals, alphanumeric tokens) are respected in the transposed code.  

---

## 8. References

- `cfd/PLAN-rename-cfd-to-cfe.md` – Rename strategy (cfe as primary, cfd as shim).  
- `cfd/SPEC.md` – Language spec (including Phase 9a agent grammar).  
- `.memory/cards.md` – Resolved issues and solutions.  
- User rules: plan before code, modules, no architecture change without review, CI/CD, REST-style integration.  
