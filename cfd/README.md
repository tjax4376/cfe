# CFE (Coding For Everyone) v2 (formerly CFD – Code for Dummies)

A natural-language programming language. Every statement is an English sentence ending with a period. Only three punctuation marks: period, comma, and space.

## Quick start

```bash
# Preferred: run with CFE
python3 -m cfe cfd/examples/showcase.cfd

# Backward-compatible CFD entrypoints (still supported)
python3 -m cfd cfd/examples/showcase.cfd
python3 cfd/cfd.py cfd/examples/showcase.cfd
```

## Language overview (see SPEC.md for full details)

### Types

```
set x to 5.
set pi to 3 point 14.
set name to text, hello world.
set flag to true.
set nothing to none.
```

### Arithmetic (PEMDAS precedence)

```
set result to 2 plus 3 times 4.
set n to negative 10.
set half to 10 divided by 2.
set r to 10 modulo 3.
```

### Comparisons

```
if x is 5 then ...
if x is not 5 then ...
if x is greater than 5 then ...
if x is less than 5 then ...
if x is at least 5 then ...
if x is at most 5 then ...
```

### Logic

```
if x is 5 and y is 10 then ...
if x is 5 or y is 10 then ...
if not x is 5 then ...
```

### Text

```
set greeting to text, hello.
set name to text, world.
set full to greeting joined with name.
set len to the length of greeting.
say greeting, name.
```

### Input

```
say text, enter your name.
ask username.
say text, hello, username.
```

### Conditions

```
if x is greater than 5 then
  say text, big.
else
  say text, small.
end.
```

### Loops

```
repeat 3 times
  say text, hello.
end.

while x is less than 10 do
  set x to x plus 1.
end.

for each i from 1 to 10 do
  say i.
end.

for each i from 0 to 20 by 2 do
  say i.
end.
```

### Loop control

```
while true do
  if done then stop. end.
  if skip_this then skip. end.
  say text, processing.
end.
```

## Running tests

```bash
python3 -m pytest cfd/tests/ -v
```

## Standalone executable

```bash
pip install pyinstaller
cd cfd && pyinstaller cfd.spec
./dist/cfd examples/showcase.cfd
```

## Requirements

- Python 3.7+
- No external dependencies (tkinter for GUI, pytest for tests)

## Architecture

```
cfd/
  __init__.py         Package marker
  __main__.py         CLI entrypoint
  lexer.py            Tokeniser
  parser.py           AST builder (precedence climbing)
  typesystem.py       Runtime type system and coercion
  interpreter.py      Statement/expression executor
  cfd_gui.py          GUI runtime (tkinter, connected later)
  cfd.py              Backward-compat wrapper
```

## Roadmap

- Phase 1: Core types, expressions, text literals, comparisons, logic (**done**)
- Phase 2: While loops, for-each range, stop/skip (**done**)
- Phase 3: Functions (define, return, call) – **planned**, see SPEC section 17.1
- Phase 4: Data structures (lists, maps)
- Phase 5: OOP (classes, instances, methods, single inheritance)
- Phase 6: Error handling (try, catch, throw)
- Phase 7: Modules and file I/O
- Phase 8: Concurrency (run, wait)

### Functions (Phase 3 – planned CFE)

Functions will bring CFE closer to C++-style free functions while keeping the
natural-language feel.

Example (not yet implemented in the interpreter):

```text
define function add with parameters a, b.
  set result to a plus b.
  return result.
end.

set x to call add with 2, 3.
say text, result is, x.
```

See `SPEC.md` section 17.1 for the full planned syntax, scoping rules, and
security notes (recursion limits, call-depth guardrails).

### Classes (Phase 5 – planned CFE)

Classes will add a simple object model on top of functions, roughly analogous to
basic C++ classes (fields, methods, single inheritance) but expressed in plain
English.

Example (not yet implemented in the interpreter):

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

See `SPEC.md` section 17.2 for the planned class and object semantics and
security notes.
