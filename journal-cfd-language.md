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
