# CFE (Coding For Everyone) – Language Specification

**Version:** 3.0 (Phase 9a – Agent Communication)  
**Punctuation:** Only period (`.`), comma (`,`), and spaces.

---

## 1. Statement terminator

Every statement ends with a **period** (`.`).

---

## 2. Types

| Type | CFE name | Examples |
|------|----------|---------|
| Integer | number | `5`, `0`, `42`, `negative 5` |
| Float | decimal | `3 point 14`, `negative 0 point 5` |
| String | text | `text, hello world` |
| Boolean | truth | `true`, `false` |
| Null | none | `none` |

---

## 3. Variables

- **Assign:** `set <name> to <expression>.`
- Names: ASCII letters only (e.g. `x`, `count`, `myVar`).
- Values: any expression (number, decimal, text, boolean, arithmetic, etc.).

```
set x to 5.
set pi to 3 point 14.
set name to text, hello world.
set flag to true.
set nothing to none.
set y to x plus 1.
```

---

## 4. Arithmetic

All arithmetic uses English words. Standard PEMDAS precedence applies.

| Operation | Syntax | Example |
|-----------|--------|---------|
| Add | `a plus b` | `set x to 5 plus 3.` |
| Subtract | `a minus b` | `set x to 10 minus 2.` |
| Multiply | `a times b` | `set x to 4 times 3.` |
| Divide | `a divided by b` | `set x to 10 divided by 2.` |
| Modulo | `a modulo b` | `set x to 10 modulo 3.` |
| Negate | `negative a` | `set x to negative 5.` |

**Precedence** (high to low):
1. `negative` (unary)
2. `times`, `divided by`, `modulo`
3. `plus`, `minus`
4. comparisons
5. `not` (unary logic)
6. `and`
7. `or`

Integer division: `10 divided by 3` yields `3` (truncates). If either operand
is a decimal, the result is a decimal.

---

## 5. Comparisons

| Comparison | Syntax |
|------------|--------|
| Equals | `x is y` |
| Not equals | `x is not y` |
| Greater than | `x is greater than y` |
| Less than | `x is less than y` |
| Greater or equal | `x is at least y` |
| Less or equal | `x is at most y` |

Comparisons return a truth value (`true` or `false`).

---

## 6. Logical operators

| Operator | Syntax |
|----------|--------|
| And | `a and b` |
| Or | `a or b` |
| Not | `not a` |

`and` and `or` short-circuit.

---

## 7. Text (strings)

Text literals are delimited by `text,` and end at the next comma or period:

```
set greeting to text, hello world.
say text, welcome to cfe.
```

**Operations:**

| Operation | Syntax | Result |
|-----------|--------|--------|
| Concatenate | `a joined with b` | Joins two values as text |
| Length | `the length of a` | Integer length of text |

```
set msg to text, hello.
set name to text, world.
set full to msg joined with text,  , joined with name.
set len to the length of msg.
```

**v2 limitation:** text literals cannot contain literal commas or periods.

---

## 8. Output

```
say <expression>.
say <expression>, <expression>, ... .
```

Multiple values separated by commas are printed space-separated on one line.

```
say text, hello world.
set x to 42.
say text, the answer is, x.
```

---

## 9. Input

```
ask <name>.
```

Reads one line from standard input. If the input looks like a number or
decimal, it is stored as that type; otherwise it is stored as text.

```
say text, enter your name.
ask username.
say text, hello, username.
```

---

## 10. Conditions

```
if <expression> then
  <statements>
else
  <statements>
end.
```

The `else` block is optional. The condition can be any expression; truthiness
rules: `0`, `0 point 0`, empty text, `none`, and `false` are falsy.

```
set x to 5.
if x is greater than 3 and x is at most 10 then
  say text, in range.
else
  say text, out of range.
end.
```

---

## 11. Repeat loop

```
repeat <expression> times
  <statements>
end.
```

The count expression is evaluated once before the loop starts.

```
set n to 3.
repeat n times
  say text, hello.
end.
```

---

## 12. While loop

```
while <expression> do
  <statements>
end.
```

The condition is re-evaluated before each iteration. The loop runs as long as
the condition is truthy.

```
set x to 0.
while x is less than 5 do
  say x.
  set x to x plus 1.
end.
```

---

## 13. For-each loop (range)

```
for each <name> from <expression> to <expression> do
  <statements>
end.
```

Iterates from start to end **inclusive**, stepping by 1.  An optional `by`
clause overrides the step:

```
for each <name> from <expression> to <expression> by <expression> do
  <statements>
end.
```

Examples:

```
for each i from 1 to 5 do
  say i.
end.

for each i from 10 to 1 by negative 1 do
  say i.
end.

for each x from 0 to 1 by 0 point 25 do
  say x.
end.
```

Start, end, and step must be numbers.  If step is positive and start > end (or
step is negative and start < end), the loop body does not execute.

---

## 14. Stop and skip (break / continue)

Use `stop.` to exit the innermost loop immediately.  Use `skip.` to jump to
the next iteration of the innermost loop.

```
set i to 0.
while true do
  set i to i plus 1.
  if i is 3 then
    skip.
  end.
  if i is 6 then
    stop.
  end.
  say i.
end.
```

Output: `1`, `2`, `4`, `5`

Using `stop` or `skip` outside of a loop is a runtime error.

---

## 15. Grammar summary

**Tokens:** words (letters or digits), period (`.`), comma (`,`), whitespace (ignored).

**Keywords:** set, to, say, ask, if, is, not, greater, than, less, at, least,
most, then, else, end, repeat, times, and, or, true, false, none, negative,
plus, minus, divided, by, modulo, text, joined, with, the, length, of, point,
while, do, for, each, from, stop, skip.

---

## 16. Security / PHA

- `ask` reads from stdin only – no file or network access.
- Expression evaluation has no `eval()` or code-injection path.
- Loop iterations capped at 1 000 000.
- Text literals are inert data – no interpolation or embedded code.
- `stop` and `skip` outside loops produce a clear runtime error.

---

## 17. Future phases and CFE roadmap

This section describes the roadmap from the current implementation toward
**CFE (Coding For Everyone)**.  
Items marked as *planned* are not yet implemented in the interpreter but have
their syntax and semantics defined here to guide future work.

### 17.1 Functions (Phase 3 – planned)

**Goal:** Add CFE functions roughly analogous to C++ free functions: named blocks
of code with parameters, local variables, and an optional return value.

#### 17.1.1 Function definitions

- Functions are defined at the top level.
- Names follow the same rules as variable names (ASCII letters only).
- Parameters are named and positional; there are no default values or
  overloading.

**Syntax:**

No parameters:

```
define function greet.
  say text, hello.
end.
```

With parameters:

```
define function add with parameters a, b.
  set result to a plus b.
  return result.
end.
```

- A function header ends with a period.
- The body is a sequence of statements, terminated by `end.`.
- A function may appear anywhere a top-level statement is allowed.

#### 17.1.2 Function calls

Functions are called from expressions. Arguments are evaluated left-to-right and
passed by value (like C++ for primitive types).

**Syntax:**

```
set x to call add with 2, 3.
say x.
```

- `call <name> with <expr> , <expr> , ...` is an expression.
- `with` and commas separate arguments.

#### 17.1.3 Return values and control flow

- `return <expression>.` returns the value of `<expression>` from the current
  function.
- `return.` (with no expression) returns `none`.
- Returning from a function exits all nested statements inside that function
  (including loops and conditionals in the body), but **does not** exit the
  caller.

#### 17.1.4 Scoping and environment model

- Each function call creates a new **local environment** for its parameters and
  local variables.
- Within a function body:
  - Reads prefer locals, then fall back to globals.
  - Assignments (`set <name> to ...`) bind to the nearest existing definition;
    if the name does not exist locally, it is created as a local.
- Global variables (set outside any function) remain visible but should be used
  sparingly.
- Recursive calls are allowed but must be guarded by a **maximum call depth**
  (implementation-defined, e.g. 1000).

#### 17.1.5 Security / PHA notes (functions)

- **Hazard:** Unbounded recursion can exhaust the call stack or CPU.
  - **Mitigation:** The interpreter must enforce a maximum call depth and raise
    a clear runtime error when exceeded.
- **Hazard:** Functions used as unbounded loops can cause denial-of-service.
  - **Mitigation:** Combine call-depth limits with existing loop-iteration
    limits; document these limits in user-facing docs.
- **Hazard:** Confusing global vs local variables can lead to unintended data
  sharing.
  - **Mitigation:** Prefer locals by default, and document the resolution rules
    clearly here and in the README.

### 17.2 Classes and objects (Phase 5 – planned)

**Goal:** Introduce a simple CFE class model inspired by C++ classes:
named types with fields and methods, plus single inheritance, expressed in
natural language.

#### 17.2.1 Class definitions

- Classes are defined at the top level.
- Names follow the same rules as variables and functions.
- A class may optionally extend a single base class.

**Syntax (no base class):**

```text
define class counter.
  define field value.

  define method increment.
    set value to value plus 1.
  end.
end.
```

**Syntax (with base class):**

```text
define class savings_counter extends counter.
  define field interest_rate.

  define method apply_interest.
    set value to value plus value times interest_rate.
  end.
end.
```

- A class header ends with a period.
- The body contains field and method declarations, then ends with `end.`.
- `define field <name>.` declares an instance field with initial value `none`.
- `define method <name> [with parameters ...].` declares an instance method;
  the body is a block of statements terminated by `end.`.

#### 17.2.2 Instances and field access

- `new <ClassName>` creates a new instance with all fields initialised to `none`
  (or to values specified by a future constructor mechanism).

**Syntax:**

```text
set c to new counter.
set the value of c to 10.
say the value of c.
```

- `new <ClassName>` is an expression.
- `the <field> of <expression>` is an expression that reads a field value.
- `set the <field> of <expression> to <expr>.` assigns to a field.

If the class or field does not exist, or the expression is not an instance of a
class, the interpreter must raise a clear runtime error.

#### 17.2.3 Methods and dispatch

- Methods are called with an implicit receiver (similar to `this`/`self` in
  other languages).
- Inside a method body:
  - `self` refers to the current instance.
  - Fields can be accessed either via `value` (preferred) or `the value of self`
    depending on implementation details.

**Syntax:**

```text
define class counter.
  define field value.

  define method increment.
    set value to value plus 1.
  end.
end.

set c to new counter.
call increment on c.
say the value of c.
```

- `call <method> on <expression> [with <args> ...]` is an expression.
- Methods are resolved dynamically based on the runtime class of the instance.
- Inherited methods can be overridden in subclasses.

#### 17.2.4 Security / PHA notes (classes)

- **Hazard:** Large or cyclic object graphs can increase memory usage.
  - **Mitigation:** Rely on Python’s GC, document typical safe patterns, and
    avoid exposing raw references outside CFE semantics.
- **Hazard:** Confusing field access vs globals can lead to subtle bugs.
  - **Mitigation:** Encourage `self`-centric patterns in docs and make field
    access syntax explicit (`the value of c`).
- **Hazard:** Inheritance hierarchies can become deep and hard to reason about.
  - **Mitigation:** Restrict to single inheritance and discourage deep chains in
    educational material.

### 17.3 Other phases (planned)

- Phase 4: Data structures (lists, maps).
- Phase 6: Error handling (try, catch, throw).
- Phase 7: Modules and file I/O.
- Phase 8: Concurrency (run, wait).

---

## 18. Agent communication (Phase 9a)

**Goal:** Extend CFE with agent communication primitives so that CFE scripts
can orchestrate conversations with AI agents from multiple vendors.  The design
mirrors CFE's existing console I/O model – `say`/`ask` for humans,
`tell`/`hear` for agents.

### 18.1 New keywords

`agent`, `tell`, `hear`, `chat`, `open`, `close`, `within`, `seconds`,
`define`, `payload`, `status`, `tokens`, `model`, `error`.

The lexer requires **no changes** – all keywords are standard WORDs.

### 18.2 Agent declaration

```
define agent <name>.
```

Binds a symbolic name to an agent whose vendor, model, API key, and system
prompt are specified in an external configuration file (`agents.yaml`).
Agent names follow variable-naming rules (ASCII letters only).

```
define agent searcher.
define agent writer.
```

Declaring an agent that is not present in the configuration file is a runtime
error.

### 18.3 Chat sessions

```
open chat <name>.
  <statements>
close chat.
```

A chat session groups a sequence of `tell`/`hear` exchanges.  The gateway
maintains conversation history per session so agents can reference prior
turns.

- `<name>` is a session identifier (ASCII letters only).
- Statements inside the chat block execute in order.
- When `close chat.` is reached, the session history is discarded.
- Chat blocks may contain any valid CFE statement, including control flow.
- Chat blocks may not be nested.

### 18.4 Tell (send message to agent)

**Simple form** – send a text expression:

```
tell <agent> <expression>.
```

**Block form** – send a structured message:

```
tell <agent>.
  set <key> to <value>.
  ...
end.
```

In the block form, variables set inside the `tell` block become the message
payload (a flat key-value map).  The block creates a temporary scope; the
enclosing environment is not modified.

### 18.5 Hear (receive response from agent)

```
hear from <agent> as <name>.
```

Blocks until the agent responds.  The response is stored in `<name>` as a
response object whose fields can be accessed with field-access expressions.

**With timeout (Phase 9b):**

```
hear from <agent> as <name> within <expression> seconds.
```

If the timeout elapses without a response, the status field of the response
is `"timeout"`.

### 18.6 Response field access

The `the <field> of <expression>` syntax reads a named field from a response
object.  Supported fields:

| Field | Type | Meaning |
|-------|------|---------|
| `payload` | text | The agent's response content |
| `status` | text | `"success"`, `"error"`, or `"timeout"` |
| `tokens` | number | Token count for the response |
| `model` | text | Which model produced the response |
| `error` | text or none | Error message, or `none` on success |

```
hear from searcher as result.
say the payload of result.
say the status of result.
say the tokens of result.
```

This syntax is forward-compatible with Phase 5's `the <field> of <expr>`
for class instances.

### 18.7 External configuration

Agent details are stored in `agents.yaml`, never in CFE scripts:

```yaml
agents:
  searcher:
    vendor: openai
    model: gpt-4o
    api_key_env: OPENAI_API_KEY
    system_prompt: "You are a search assistant."
    max_tokens: 1000
    temperature: 0.3
```

- `vendor` – adapter name (`openai`, `anthropic`, `google`, `local`, `http`).
- `model` – model identifier.
- `api_key_env` – environment variable holding the API key.
- `system_prompt` – injected as the system message for every conversation.
- `max_tokens` – maximum tokens per response.
- `temperature` – sampling temperature (0.0–2.0).

### 18.8 Complete example

```
define agent searcher.
define agent writer.

open chat tutorial.
  tell searcher.
    set intent to text, search.
    set query to text, python asyncio tutorial.
    set limit to 3.
  end.
  hear from searcher as searchresult.

  if the status of searchresult is text, error then
    say text, search failed.
    say the error of searchresult.
  else
    tell writer.
      set intent to text, summarize.
      set context to the payload of searchresult.
      set format to text, markdown.
    end.
    hear from writer as summary.
    say the payload of summary.
  end.
close chat.
```

### 18.9 Grammar additions

**New statement forms:**

```
define agent <name>.
open chat <name>. <stmts> close chat.
tell <agent> <expr>.
tell <agent>. <stmts> end.
hear from <agent> as <name>.
```

**New expression forms:**

```
the payload of <expr>
the status of <expr>
the tokens of <expr>
the model of <expr>
the error of <expr>
```

**Updated keywords list:** set, to, say, ask, if, is, not, greater, than,
less, at, least, most, then, else, end, repeat, times, and, or, true, false,
none, negative, plus, minus, divided, by, modulo, text, joined, with, the,
length, of, point, while, do, for, each, from, stop, skip, **define, agent,
tell, hear, chat, open, close, within, seconds, payload, status, tokens,
model, error**.

### 18.10 Security / PHA (agent communication)

- **Hazard:** API key exposure in scripts.
  - **Mitigation:** Keys are referenced by environment variable name in
    external YAML config, never embedded in CFE source.
- **Hazard:** Unbounded message loops (agent A instructs agent B instructs
  agent A …).
  - **Mitigation:** Maximum message depth limit (configurable, default 50).
- **Hazard:** Network failures causing script hangs.
  - **Mitigation:** Default timeout on `hear` (30 s), explicit `within`
    syntax in Phase 9b.
- **Hazard:** Prompt injection via message forwarding.
  - **Mitigation:** Message payloads are treated as data fields, not
    executable code.  The gateway separates system prompts from user data.
- **Hazard:** Large payloads causing memory exhaustion.
  - **Mitigation:** Configurable payload size limits in gateway config.
- **Hazard:** Agent impersonation.
  - **Mitigation:** Agents must be declared with `define agent` and match a
    config entry.  No dynamic agent creation at runtime.
- **Hazard:** Cost runaway from excessive API calls.
  - **Mitigation:** Token counting via `the tokens of`, configurable
    per-session token limits in gateway config.
- **Hazard:** Network access from the interpreter.
  - **Mitigation:** All network I/O is delegated to the gateway module.  The
    interpreter calls gateway Python functions; it does not make HTTP requests
    directly.
