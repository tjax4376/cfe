# Memory Cards – Issues & Solutions

*Resolved issues and solutions to avoid recurrence.*

---

## 1. `types.py` shadows stdlib `types` module

**Issue:** Naming the CFD type system `cfd/types.py` causes `ImportError` when Python's stdlib tries to import its own `types` module — they collide on `sys.path`.

**Solution:** Renamed to `cfd/typesystem.py`. Never name project modules the same as stdlib modules (`types`, `os`, `sys`, `re`, etc.).

---

## 2. `times` keyword ambiguity (arithmetic vs repeat block)

**Issue:** `repeat n times say hello. end.` — the parser's expression engine greedily consumed `times` as the multiplication operator, eating the loop body as operands.

**Solution:** Added `_stop_words` set to the parser. `_parse_repeat` sets `{"times"}` as a stop word; `_parse_mul` checks stop words before consuming `times`. Restored after parsing the count expression.

---

## 3. Lexer splits alphanumeric tokens

**Issue:** `v2` in text becomes `v 2` because the lexer regex `[a-zA-Z]+|[0-9]+` matches letters and digits separately.

**Solution:** Documented as v1 limitation. In text literals, use full words (e.g. `version two` instead of `v2`). May support `[a-zA-Z0-9]+` word tokens in a future phase.

---

## 4. Text literals cannot contain commas or periods

**Issue:** `text,` starts a literal that ends at the next COMMA or PERIOD. So text content cannot include those characters.

**Solution:** Documented as v1 limitation. Use variables and `joined with` for complex strings. Future phases may add escape sequences.

---

## 5. Use `python3` not `python` for CLI

**Issue:** `python` is not always on PATH (macOS exit 127).

**Solution:** Always use `python3` in docs, scripts, and examples.

---

## 6. Context-sensitive `_stop_words` must apply globally in expression parser

**Issue:** Originally `_stop_words` only blocked "times" in `_parse_mul`. When adding `for each ... from <expr> to <expr> by <expr> do`, the keywords "to" and "by" needed to stop expression parsing in their respective contexts.

**Solution:** Extended `_stop_words` checks to `_parse_atom` (prevents stop-words from becoming VarRef) and `_at_expr_boundary` (prevents expression continuation past stop-words). This makes the mechanism general for any future context-sensitive keyword.

---

## 7. `divided by` inside stop-word context works because `_expect_word` is greedy

**Issue:** In `for each i from 1 to 10 divided by 2 do`, with "by" as a stop-word for the end expression, there was concern that "by" in "divided by" would be blocked.

**Solution:** No conflict exists. `_parse_mul` first matches "divided", then calls `_expect_word("by")` which unconditionally consumes the next word. The `_stop_words` check in `_parse_atom` is never reached because "by" is consumed by the explicit expect call, not by the variable-reference fallback.

---

## 8. Loop signals (stop/skip) must propagate through `run()` for nested control flow

**Issue:** `stop.` inside an `if` inside a loop must propagate through the if-body's `run()` call to reach the enclosing loop handler. Catching signals in `run()` would intercept them prematurely.

**Solution:** `run()` does NOT catch signals. Only loop handlers in `_exec_stmt` catch `_StopSignal`/`_SkipSignal`. A separate `execute()` function wraps the top-level call and converts stray signals to `CfdRuntimeError`.
