# Journal: CFD → CFE Transpose Plan

## Session – Plan: Review CFD and Transpose Core into CFE (2025-03-14)

**Context:** User requested a plan that (1) reviews what is created in the `cfd` folder, and (2) ensures that the core functionality is transposed into the `cfe` folder. Currently, CFD holds the full language implementation (lexer, parser, typesystem, interpreter, GUI) while CFE is a thin shim that re-exports from CFD; CFE also owns the agent stack (`cfe/agent/`), and the CFD interpreter already depends on `cfe.agent.gateway`.

**Discussion points:**
- **Scope of “core”:** Lexer, parser, typesystem, interpreter, and GUI. Agent grammar and execution stay in the interpreter; only the gateway implementation lives in `cfe/agent/`.
- **Transpose meaning:** Copy implementation from `cfd` into `cfe` and fix imports so CFE is self-contained; then turn CFD into a thin shim (per existing `cfd/PLAN-rename-cfd-to-cfe.md`).
- **Vibe-check (user-vibe-check-mcp):** Plan was validated with metacognitive questions:
  1. Does the plan directly address the user request? Yes – review cfd, transpose core into cfe.
  2. Is there a simpler approach? Option to keep tests in `cfd/tests` and only switch imports to `cfe` (fewer file moves).
  3. Unstated assumptions? Plan assumes “transpose” implies copy-into-cfe-then-shim-cfd; user asked for a “plan” only, so no code until review.
  4. Alignment with user intent: Plan first; implementation only after clarification in chat (test location, versioning, SPEC location, standalone executable, cards.md).
- **User rules:** No code without reviewed plan; modules; no architecture decision without review; single CI/CD; core–module integration via APIs (already satisfied by interpreter → gateway).

**Summary of code changed:**
- **Plan only – no code changes.** Created:
  - `PLAN-cfd-to-cfe-transpose.md` – Full plan: audit of cfd contents, definition of core, step-by-step transpose strategy (copy into cfe → update CFE __main__ → tests → CFD shims → docs/build), clarification questions for review, success criteria, and references to SPEC, cards.md, and rename plan.
- **Journal:** This file (`journal-cfd-to-cfe-transpose.md`) recording context, discussion, and summary.
- **Next steps:** Resolve clarification questions in chat (Section 5 of the plan); then implement in order per plan Section 4.3.

---

## Session 2 – Implementation (2025-03-14)

**Context:** User confirmed: (1) Option A – tests in cfe; (2) All CFD→CFE, folders cfd→cfe-0.1, cfe→cfe-0.2; (3) Move SPEC and README to cfe/; (4) Build cfe only; (5) CFE should not behave differently.

**Discussion points:**
- Package names: Python module names cannot contain hyphens, so `cfe-0.2` contains package `cfe`, and `cfe-0.1` contains package `cfe_0_1` (shim re-exporting cfe).
- Run CFE with `PYTHONPATH=cfe-0.2 python3 -m cfe <file>` from repo root.
- All 182 tests pass with cfe-0.2 implementation; CLI runs examples correctly.

**Summary of code changed:**
- **cfe-0.2/cfe/** – Full implementation: lexer.py, parser.py, typesystem.py (CfeType), interpreter.py (CfeRuntimeError), cfe_gui.py, __init__.py (__version__ 0.2.0), __main__.py; agent/ copied from cfe; SPEC.md and README.md moved and CFD→CFE text replaced; examples/ and tests/ with imports cfd→cfe, CfdRuntimeError→CfeRuntimeError.
- **cfe-0.1/cfe_0_1/** – Shim: __init__.py and __main__.py re-export/forward to cfe (requires cfe-0.2 on PYTHONPATH).
- **cfe-0.2/** – cfe.spec, cfe_run.py, build_standalone.sh for building single `cfe` executable only.
- **PLAN-cfd-to-cfe-transpose.md** – Section 5 updated with resolved decisions and status set to Implemented.
- Original `cfd/` and `cfe/` folders left in place; user may rename or remove them separately.
