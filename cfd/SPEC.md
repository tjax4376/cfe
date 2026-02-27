# CFD (Code for Dummies) – Language Specification

**Version:** 2.1 (Phase 2)  
**Punctuation:** Only period (`.`), comma (`,`), and spaces.

---

## 1. Statement terminator

Every statement ends with a **period** (`.`).

---

## 2. Types

| Type | CFD name | Examples |
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
say text, welcome to cfd.
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

## 17. Future phases

- Phase 3: Functions (define, return, call).
- Phase 4: Data structures (lists, maps).
- Phase 5: OOP (describe, create, methods, inheritance).
- Phase 6: Error handling (try, catch, throw).
- Phase 7: Modules and file I/O.
- Phase 8: Concurrency (run, wait).
