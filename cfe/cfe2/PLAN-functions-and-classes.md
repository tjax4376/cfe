# Plan: Functions and Classes for CFE

**Status:** Design only (no implementation yet).  
**Scope:** Parser and interpreter changes to support CFE functions and a simple
class model on top of the existing CFD v2 core.

---

## 1. Goals and constraints

- Bring the language closer to core C++ by adding:
  - Free functions (parameters + return values).
  - A class/object model (fields, methods, single inheritance).
- Keep the existing architecture:
  - `lexer.py` unchanged (words, commas, periods only).
  - `parser.py` builds a richer AST.
  - `interpreter.py` remains a tree-walk interpreter with a small type system.
- Maintain:
  - Simple, natural-language syntax consistent with `SPEC.md`.
  - Clear security limits (loop iteration cap, call-depth cap).
  - Testability and backwards compatibility for existing CFD v2 programs.

---

## 2. Parser changes (high level)

### 2.1 New AST nodes (expressions)

- `CallExpr(Expr)` – function calls:
  - Fields: `name: str`, `args: list[Expr]`, `line: int`.
  - Constructed from syntax: `call <name> with <expr> , <expr> , ...`.

- `NewExpr(Expr)` – object allocation:
  - Fields: `class_name: str`, `line: int`.
  - Constructed from syntax: `new <ClassName>`.

- `FieldAccessExpr(Expr)` – instance field reads:
  - Fields: `target: Expr`, `field_name: str`, `line: int`.
  - Constructed from syntax: `the <field> of <expr>`.

- `MethodCallExpr(Expr)` – instance method calls:
  - Fields: `method_name: str`, `target: Expr`, `args: list[Expr]`, `line: int`.
  - Constructed from syntax: `call <method> on <expr> [with <args> ...]`.

These are all evaluated via the interpreter; the lexer remains unchanged.

### 2.2 New AST nodes (statements)

- `FunctionDef(Stmt)` – top-level function declarations:
  - Fields: `name: str`, `params: list[str]`, `body: list[Stmt]`, `line: int`.
  - Built from:
    - `define function <name>. ... end.`
    - `define function <name> with parameters <p1> , <p2> , ... . ... end.`

- `ReturnStmt(Stmt)` – returns from a function:
  - Fields: `value: Optional[Expr]`, `line: int`.
  - Built from:
    - `return <expr>.`
    - `return.`

- `ClassDef(Stmt)` – top-level class declarations:
  - Fields: `name: str`, `base_name: Optional[str]`,
    `fields: list[FieldDef]`, `methods: list[MethodDef]`, `line: int`.
  - Built from:

    ```text
    define class Name.
      define field field1.
      define method method1.
        ...
      end.
    end.

    define class Child extends Parent.
      ...
    end.
    ```

- `FieldDef(Stmt)` – class field declarations (used only inside `ClassDef`):
  - Fields: `name: str`, `line: int`.

- `MethodDef(Stmt)` – class method declarations (owned by `ClassDef`):
  - Fields: `name: str`, `params: list[str]`, `body: list[Stmt]`, `line: int`.

`FieldDef` and `MethodDef` will not be executed directly by `_exec_stmt`; they
are consumed when building class metadata in the interpreter.

### 2.3 Statement-dispatch changes

- Extend `STATEMENT_KEYWORDS` to include:
  - `define`, `return`, `class`, `field`, `method`, `extends`.
- Extend `_parse_statement`:
  - `define` → dispatch to `_parse_define`, which looks ahead to `function` or
    `class` and calls `_parse_function_def` or `_parse_class_def`.
  - `return` → `_parse_return`.
- Inside `_parse_class_def`, parse a sequence of `FieldDef` and `MethodDef`
  until `end.` is encountered, similar to `if`/`while` bodies.

### 2.4 Expression parsing integration

- Treat `call` and `new` as starts of specific atom forms:
  - In `_parse_atom`, before falling back to variable references:
    - If word is `call`, parse either:
      - `call <name> with <args>` → `CallExpr`.
      - `call <method> on <expr> [with <args>]` → `MethodCallExpr`.
    - If word is `new`, parse:
      - `new <ClassName>` → `NewExpr`.
- Treat `the <field> of <expr>` as a special atom form that yields a
  `FieldAccessExpr`.
- Ensure `_stop_words` and `STRUCTURAL_KEYWORDS` still correctly delimit
  expressions (e.g. `then`, `do`, `end`, etc.).

### 2.5 Set statement enhancements (field assignment)

- Extend `_parse_set` to support:

```text
set <name> to <expr>.
set the <field> of <expr> to <expr>.
```

- Represent field-assignment targets either by:
  - Reusing `FieldAccessExpr` as the `name`-like part of `SetStmt`, or
  - Introducing a small `AssignmentTarget` union type.
- Interpreter will detect field targets and route them through the
  object/field machinery instead of plain variables.

---

## 3. Interpreter changes (high level)

### 3.1 Function model

- Maintain a **function table**:
  - `functions: dict[str, FunctionDef]`, built during a first pass over the
    top-level statement list before execution (or lazily populated).
  - Detect and report duplicate function names as a runtime error.

- Introduce a **call stack** and lexical environments:
  - Replace the single flat `env: dict[str, Any]` with either:
    - A linked chain of environments, or
    - A list/stack of `Frame` objects (`locals`, optional `closure`, optional
      `self`).
  - Implement a helper to resolve variables:
    - Search innermost frame first, then outer frames, then a global frame.

- Add a `CallDepthLimitError` (or reuse `CfdRuntimeError`) triggered when the
  call depth exceeds a configured maximum (e.g. 1000).

- Implement evaluation for `CallExpr`:
  - Look up the `FunctionDef` by name.
  - Evaluate arguments left-to-right.
  - Create a new frame binding parameters to argument values.
  - Execute the function body until:
    - A `ReturnStmt` is encountered, or
    - The end of the body is reached (implicit `none`).

- Introduce an internal `_ReturnSignal` exception used only to unwind from a
  function body without interfering with loop signals.

### 3.2 Class and object model

- Maintain a **class table**:
  - `classes: dict[str, ClassMeta]`, built from `ClassDef` nodes.
  - `ClassMeta` contains:
    - `name`, `base` (reference to parent `ClassMeta` or `None`),
    - `fields` (list or set of field names, including inherited ones),
    - `methods` (mapping method name → `MethodDef`, supporting override).

- Define an **instance representation**:
  - Likely a small Python class or `dict` with:
    - `__cfe_class__` pointing to `ClassMeta`.
    - `__fields__` mapping field names to values.
  - Provide helper functions:
    - `is_instance(value) -> bool`
    - `get_field(instance, name)`
    - `set_field(instance, name, value)`

- Implement evaluation for:
  - `NewExpr`:
    - Look up the class.
    - Create an instance with all fields initialised to `none`.
  - `FieldAccessExpr`:
    - Evaluate the target expression.
    - Validate it is an instance.
    - Read the field or raise a runtime error.
  - Field assignment in `_exec_stmt`:
    - Detect `set the <field> of <expr>` targets and route them to `set_field`.

- Implement evaluation for `MethodCallExpr`:
  - Evaluate the target expression to an instance.
  - Look up the method on the instance class (respecting inheritance).
  - Evaluate arguments.
  - Call the method as a function with an implicit `self` parameter bound to
    the instance plus any additional parameters from the call.

- Reuse the function call-stack machinery:
  - Methods are implemented as functions with a `self` local.
  - `ReturnStmt` works the same inside functions and methods.

### 3.3 Error handling and limits

- All new runtime errors are surfaced as `CfdRuntimeError` with clear messages:
  - Calling undefined functions or methods.
  - Constructing undefined classes.
  - Accessing undefined fields.
  - Passing wrong numbers of arguments.
  - Exceeding maximum call depth.
- Loop signals (`_StopSignal`, `_SkipSignal`) continue to work inside functions
  and methods, but only affect the innermost loop in the current frame.

---

## 4. Testing strategy (overview)

- New test modules:
  - `tests/test_functions.py`
  - `tests/test_classes.py`
- Coverage:
  - Correct parsing of function and class declarations.
  - Successful calls (plain, nested, recursive) with correct results.
  - Field and method behaviour across inheritance hierarchies.
  - Failure cases (undefined names, type mismatches, depth limits).
- Keep existing 109 tests green to preserve CFD v2 behaviour.

---

## 5. Security and robustness notes

- Enforce:
  - Maximum loop iterations (already implemented).
  - Maximum call depth (new).
- Avoid:
  - Any dynamic `eval()` or execution of user text beyond the CFE interpreter.
- Make sure errors are never silently ignored:
  - Either raise `CfdRuntimeError` or a narrowly scoped internal signal caught
    at a well-defined boundary (loops, function/method returns).

