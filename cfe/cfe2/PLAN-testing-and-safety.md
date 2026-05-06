# Plan: Testing, PHA/STRIDE, and Safety for CFE Evolution

**Status:** Design only (no implementation yet).  
**Scope:** Define test coverage and safety practices for new functions, classes,
and the CFD→CFE rename.

---

## 1. Testing strategy overview

- Keep all existing CFD v2 tests passing (baseline regression suite).
- Add focused tests for:
  - Functions (`tests/test_functions.py`):
    - Simple functions (no params, with params).
    - Nested calls and recursion (including depth-limit failures).
    - Interaction with loops and conditionals.
    - Error cases (undefined functions, wrong arity, type mismatches).
  - Classes (`tests/test_classes.py`):
    - Instance creation, field defaults, and field assignment.
    - Method calls, including methods that mutate fields.
    - Single inheritance and method overriding.
    - Error cases (undefined classes/fields/methods, wrong receiver type).
  - Rename and shims (`tests/test_cfe_shim.py` or similar):
    - `python3 -m cfe` and `python3 -m cfd` both run the same program.
    - Shims correctly forward imports and CLI entrypoints.

---

## 2. PHA/STRIDE-style considerations

### 2.1 Functions

- **Denial of Service (DoS) via recursion:**
  - Risk: Deep or infinite recursion can consume CPU and stack.
  - Mitigation:
    - Enforce a maximum call depth (e.g. 1000).
    - Raise a clear runtime error when exceeded.
    - Add tests that deliberately exceed the limit and assert on the error.

- **Information integrity:**
  - Risk: Confusion between global and local variables can corrupt shared state.
  - Mitigation:
    - Prefer locals by default; document variable-resolution rules.
    - Add tests covering local shadowing and global access patterns.

### 2.2 Classes and objects

- **Resource usage:**
  - Risk: Large numbers of instances or deep object graphs may increase memory
    usage.
  - Mitigation:
    - Rely on Python’s GC; avoid holding unnecessary global references.
    - Add tests that create many instances and ensure they behave predictably.

- **Tampering and misuse:**
  - Risk: Confusing field vs global variables or mutating shared instances.
  - Mitigation:
    - Make field access syntax explicit (`the value of c`).
    - Test both correct and incorrect field access patterns.

### 2.3 Rename and shims

- **Spoofing/confusion:**
  - Risk: Users may be unsure whether `cfd` or `cfe` is authoritative.
  - Mitigation:
    - Clearly document that `cfe` is the primary entrypoint going forward.
    - Keep `cfd` as a thin, well-documented shim only.

- **Elevation / privilege issues:**
  - Not applicable in current scope (no file/network IO yet).
  - Future IO features must add specific PHA/STRIDE notes.

---

## 3. Safety practices during implementation

- Do not suppress errors:
  - All unexpected runtime conditions should raise `CfdRuntimeError` (or future
    `CfeRuntimeError`) with clear messages.
- Keep limits explicit and centralised:
  - Loop limit (`MAX_LOOP_ITERATIONS`) and call-depth limit should be defined
    in one place and referenced from docs and tests.
- Avoid new external dependencies unless:
  - Their licenses and security implications are understood and documented.

