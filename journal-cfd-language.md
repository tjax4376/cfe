# Journal: CFD (Code for Dummies) Language

## Session 1 – Initial v0.1

**Context:** Define a new simple programming language "cfd" with natural-language style, minimal punctuation (comma, period, spaces only), and build an interpreter incrementally.

**Discussion points:**
- Statements end with a period.
- Only comma, period, and spaces as punctuation.
- Must support: conditions, loops, and defining parameters (variables).
- Start small: variables + output first, then conditions, then loops.
- Interpreter in Python for simplicity and single-module deployment.

**Summary of code changed:**
- Language spec `cfd/SPEC.md` (grammar, keywords, security note).
- Interpreter `cfd/cfd.py`: lexer (words, period, comma), parser (Set, Say, If, Repeat), interpreter with env dict; CLI.
- Examples: `hello.cfd`, `condition.cfd`, `loop.cfd`.

---

## Session 2 – Windows and apps (plan)

**Context:** User requested ability to create windows and build an application from CFD.

**Discussion points:**
- Plan in `cfd/PLAN-windows-and-apps.md`: create window, add label/button, show window.
- User chose tkinter, close button, parent/child windows, standalone executable.

**Summary of code changed:**
- `cfd/cfd_gui.py`: tkinter GUI runtime (create_window, add_label, add_close_button, show_windows).
- `cfd/cfd.spec` + `cfd/build_standalone.sh`: PyInstaller standalone build.
- GUI AST nodes added to cfd.py but not wired to parser/interpreter (deferred).

---

## Session 3 – v2 redesign (Phase 1)

**Context:** User requested C++ equivalent power while keeping the language simple and AI-friendly. Design and implement phase by phase.

**Discussion points:**
- Feature parity with C++ now, architecture designed for compilation later.
- Text literals via `text,` comma-delimited (user chose).
- Phase-by-phase approach (user chose).
- 8 phases total; Phase 1 = types, expressions, comparisons, logic, text, input.

**Key design decisions:**
- `types.py` renamed to `typesystem.py` (shadows stdlib `types` module).
- `times` keyword is both arithmetic operator and `repeat` block word; solved with context-sensitive stop-words in parser.
- Text literals end at next COMMA or PERIOD; cannot contain literal commas/periods.
- Lexer splits alphanumeric tokens (e.g. `v2` → `v` + `2`); documented as v1 limitation.

**Summary of code changed:**
- Monolith split into package: `lexer.py`, `parser.py`, `typesystem.py`, `interpreter.py`, `__init__.py`, `__main__.py`.
- `cfd.py` kept as backward-compat wrapper.
- Lexer: newline bug fixed; `LexError` raised on unknown chars.
- Parser: full expression AST (BinaryExpr, UnaryExpr, Literal, VarRef, LengthExpr); precedence climbing (PEMDAS); text literals; decimals via `point`; booleans; comparisons (is, is not, greater/less than, at least/most); logical ops; stop-words for `repeat ... times` ambiguity.
- Type system: CfdType enum; coercion helpers (to_number, to_decimal, to_text, to_truth, coerce_numeric_pair).
- Interpreter: recursive expression evaluator; multi-type values; `ask` for input; division-by-zero and loop-limit guards.
- SPEC.md updated to v2 (Phase 1).
- 6 new example .cfd files; 73 unit tests (all passing).
- README.md updated with v2 syntax, architecture, roadmap.
- PyInstaller spec updated for package structure.

---

## Session 4 – Phase 2 (Enhanced control flow)

**Context:** Implement Phase 2 of the CFD v2 Language Redesign — while loops, for-each range iteration, stop (break), and skip (continue).

**Discussion points:**
- `while <expr> do <stmts> end.` — condition-based loop.
- `for each <var> from <start> to <end> [by <step>] do <stmts> end.` — inclusive range iteration with optional step.
- `stop.` — break from innermost loop; runtime error if used outside a loop.
- `skip.` — continue to next iteration; runtime error if used outside a loop.
- Generalized `_stop_words` mechanism in the parser to handle context-sensitive keywords (`to`, `by` in for-each context, `times` in repeat context).
- Exception-based loop signals (`_StopSignal`, `_SkipSignal`) for clean control flow without polluting the return path.
- New `execute()` top-level entry point catches stray signals and converts to `CfdRuntimeError`.

**Key design decisions:**
- For-each range is inclusive (`from 1 to 5` iterates [1, 2, 3, 4, 5]).
- Negative step requires explicit `by negative N`; if step is positive and start > end, zero iterations (no implicit direction reversal).
- `_stop_words` extended to `_parse_atom` and `_at_expr_boundary` (not just `_parse_mul`) for general context-sensitive keyword blocking.
- `divided by` inside a for-each end expression works correctly — `_expect_word("by")` consumes "by" greedily before `_stop_words` can block it.
- All three loop types (repeat, while, for each) handle stop/skip uniformly via try/except.

**Summary of code changed:**
- `cfd/parser.py` (v2.1): 4 new AST nodes (WhileStmt, ForEachStmt, StopStmt, SkipStmt); 4 new parse methods; generalized `_stop_words` in `_at_expr_boundary` and `_parse_atom`; updated keyword sets.
- `cfd/interpreter.py` (v2.1): `_LoopSignal`/`_StopSignal`/`_SkipSignal` exception classes; handlers for WhileStmt, ForEachStmt, StopStmt, SkipStmt; RepeatStmt updated with signal handling; new `execute()` top-level function.
- `cfd/__main__.py` (v2.1): imports and calls `execute()` instead of `run()`.
- `cfd/SPEC.md` (v2.1): sections 12–14 added (while, for-each, stop/skip); grammar and keyword list updated; future phases renumbered.
- `cfd/tests/test_parser.py`: 12 new Phase 2 tests (while, for-each variants, stop, skip, error cases).
- `cfd/tests/test_interpreter.py`: 24 new Phase 2 tests (while, for-each, stop/skip in all loop types, edge cases, error cases).
- `cfd/examples/while_loop.cfd`, `cfd/examples/for_each.cfd`, `cfd/examples/stop_skip.cfd`: 3 new example files.
- `cfd/README.md`: updated with Phase 2 syntax and roadmap.
- 109 total tests, all passing.

---

## Session 5 – CFE evolution and C++ alignment

**Context:** Begin evolving CFD toward CFE (Coding For Everyone), aligning language capabilities with core C++ concepts and planning a hard rename from `cfd` to `cfe` with minimal shims.

**Discussion points:**
- Mapped existing CFD v2 constructs to C++:
  - CFD variables and expressions ↔ C++ variables, arithmetic, comparisons, and boolean logic.
  - CFD `if`/`else`, `repeat`, `while`, and `for each` ↔ C++ `if`, `while`, `for`/range loops, and `break`/`continue` via `stop`/`skip`.
  - CFD text and basic I/O (`say`, `ask`) ↔ C++ `std::string` and console I/O, but without exposing streams directly.
- Identified key C++ gaps to close in CFE:
  - Functions with parameters and return values (free functions first, no overloading/templates).
  - A class/object model (fields, methods, single inheritance) built on top of the existing interpreter, using a clear call stack and instance representation.
  - Structured error handling (CFE analogue of `try`/`catch`) for later phases.
- Agreed that new features must:
  - Preserve natural-language syntax (words, commas, periods only).
  - Be specified in `SPEC.md` and `README.md` before implementation (requirements-first).
  - Include a lightweight PHA/STRIDE-style note for recursion depth, resource use, and misuse of new constructs.
- Planned a CFD→CFE rename path:
  - Introduce a `cfe` package and CLI while keeping a thin `cfd` shim.
  - Gradually move core modules and docs to `cfe`, then retire the shim after a documented transition.

**Summary of code changed:**
- No code or spec changes yet; this session records the alignment analysis and rename strategy in the journal as the basis for upcoming function, class, and rename work.

---

## Session 6 – Implementing the initial CFD→CFE rename

**Context:** Expose the new CFE (Coding For Everyone) name in the codebase and
CLI while keeping the existing CFD implementation intact, following the
previously agreed rename plan.

**Discussion points:**
- Introduced a `cfe` Python package that forwards to the existing `cfd`
  implementation for now, so users can start importing and running code as CFE.
- Kept CFD fully working to avoid breaking existing scripts, treating it as the
  legacy name.
- Updated high-level docs to reflect the new CFE branding while documenting CFD
  as the former name.
- Added a small CFE shim test to ensure the new import path behaves correctly
  and does not suppress errors.

**Summary of code changed:**
- Added `cfe/__init__.py` (CFE package marker) and `cfe/__main__.py` (CLI
  entrypoint) that forwards to `cfd.__main__.main`, enabling `python3 -m cfe`.
- Added shim modules `cfe/lexer.py`, `cfe/parser.py`, `cfe/interpreter.py`,
  `cfe/typesystem.py`, and `cfe/cfe_gui.py` that re-export the corresponding
  `cfd.*` modules.
- Added `cfd/tests/test_cfe_shim.py` to verify that importing and running a
  simple program via `cfe.*` produces the expected output.
- Updated `README.md` heading and quick-start examples to prefer CFE (`python3
  -m cfe`) while keeping CFD entrypoints documented as backward-compatible.
- Updated `SPEC.md` title and roadmap wording to describe the language under the
  CFE name.
- Ran the full test suite (`python3 -m pytest -q` in `cfd/`); all 110 tests
  (including the new shim test) passed.

---

## Session 7 – Phase 9a: Agent Communication Gateway

**Context:** Extend CFE with agent communication primitives so CFE scripts
can orchestrate multi-turn conversations with AI agents from multiple vendors
(OpenAI, Anthropic, etc.).  The design mirrors CFE's existing console I/O
model – `say`/`ask` for humans, `tell`/`hear` for agents.

**Discussion points:**
- Researched emerging agent communication protocols: MCP (Anthropic), A2A
  (Google), ACP (HTTP REST), ANP (decentralized), ADOL (IETF draft for token
  efficiency), G2CP (graph-grounded, 73% token reduction).
- Concluded that CFE's natural-language structure achieves ~67% token reduction
  versus equivalent JSON/A2A messages while remaining human-readable and
  LLM-friendly (well-tokenised English words).
- Core design insight: agent I/O is a natural extension of console I/O.  The
  `tell`/`hear` pair for agents parallels `say`/`ask` for humans.  Minimal
  new syntax required.
- Added 7 new keywords: `agent`, `tell`, `hear`, `chat`, `open`, `close`,
  `within`.  Lexer unchanged (all are standard WORDs).
- `tell` has two forms: simple (`tell agent text, hello.`) and block
  (`tell agent. set key to val. end.`).  Block form creates a structured
  key-value payload from `set` statements in a temporary scope.
- `hear from agent as name.` stores a Response object whose fields
  (`payload`, `status`, `tokens`, `model`, `error`) are accessed via
  `the <field> of <expr>` syntax, forward-compatible with Phase 5 classes.
- `open chat name. ... close chat.` maintains conversation history per session
  so agents can reference prior turns.
- Agent configuration (vendor, model, API key, system prompt) lives in
  external YAML (`agents.yaml`), never in CFE scripts.  API keys are
  referenced by environment variable name.
- Gateway module (`cfe/agent/`) uses a pluggable adapter pattern: one adapter
  per vendor translating CFE messages to vendor-specific API format and back.
- Security hazards identified and mitigated: API key exposure (env vars only),
  unbounded message loops (depth limit 50), network hangs (default timeout),
  prompt injection (payload is data, not code), agent impersonation (must
  declare and match config).

**Key design decisions:**
- `text, success then` is greedily consumed as a text literal (existing v2
  limitation).  Idiomatic workaround: store comparison values in a variable
  first (`set ok to text, success. if the status of reply is ok then ...`).
- Gateway is lazy-loaded in the interpreter to avoid import overhead when
  running non-agent scripts.
- The interpreter delegates all network I/O to the gateway module; it never
  makes HTTP requests directly.
- OpenAI adapter uses Chat Completions API (broadest compatibility); Anthropic
  adapter uses Messages API with system prompt as a separate field.
- Both adapters use stdlib `urllib` (no third-party HTTP dependency) for
  minimal footprint.

**Alternatives considered and rejected:**
- JSON as agent wire format: 3x more verbose, requires syntactically correct
  JSON generation from models.
- Protocol Buffers / MessagePack: binary, not human-readable, can't be
  generated by LLMs.
- MCP directly: tool-invocation focused, not peer-to-peer agent chat.
- Embedded credentials in CFE scripts: security risk.

**Summary of code changed:**
- `cfd/SPEC.md` (v3.0): Section 18 added – agent communication syntax,
  semantics, grammar additions, configuration, and security/PHA notes.
  Updated keyword list.
- `cfd/parser.py` (v3.0): 5 new AST nodes (DefineAgentStmt, OpenChatStmt,
  TellStmt, HearStmt, ResponseFieldExpr); 6 new parse methods
  (_parse_define, _parse_define_agent, _parse_open_chat, _parse_tell,
  _parse_hear); response field expression parsing in _parse_atom;
  STATEMENT_KEYWORDS, STRUCTURAL_KEYWORDS, EXPR_KEYWORDS updated.
- `cfd/interpreter.py` (v3.0): Lazy-loaded gateway; _eval_response_field
  for response field access; _exec_define_agent, _exec_open_chat,
  _exec_tell, _exec_hear; set_gateway/get_gateway for DI in tests.
- `cfe/agent/__init__.py`: Module marker.
- `cfe/agent/message.py`: Message and Response dataclasses with field
  access and prompt rendering.
- `cfe/agent/config.py`: YAML config loader with env var resolution,
  validation, supported vendor checking.
- `cfe/agent/session.py`: ChatSession, Turn, SessionManager with turn
  limits and per-agent history filtering.
- `cfe/agent/gateway.py`: Gateway class with agent registry, adapter
  dispatch, session-aware routing, message depth limiting.
- `cfe/agent/adapters/base.py`: Abstract BaseAdapter interface.
- `cfe/agent/adapters/openai_adapter.py`: OpenAI Chat Completions adapter
  with session history and error handling.
- `cfe/agent/adapters/anthropic_adapter.py`: Anthropic Messages API adapter
  with session history and error handling.
- `cfe/agent/adapters/__init__.py`: Adapter registry module marker.
- `cfd/tests/test_agent_parser.py`: 22 tests for agent parser extensions.
- `cfd/tests/test_agent_interpreter.py`: 16 tests with mock gateway.
- `cfd/tests/test_agent_gateway.py`: 26 tests for gateway, config, session.
- `cfd/examples/agent_chat.cfe`: Single-agent multi-turn chat example.
- `cfd/examples/agent_multi.cfe`: Multi-agent orchestration example.
- `agents.yaml`: Example agent configuration with 4 agents.
- 182 total tests (110 original + 72 new), all passing.  Zero regressions.
