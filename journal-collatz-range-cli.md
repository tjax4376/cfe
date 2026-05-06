## Context Description

Updated `collatz_modified.py` to accept command-line range input and process Collatz sequences from `START` to `END` inclusively.

## Discussion Points

- Replaced static constants with CLI arguments.
- Added range iteration so each integer from `START` through `END` is evaluated.
- Output now shows only values that are newly calculated (no skipped-value notes).
- Added explicit reporting for any starting values that do not reach the `4 -> 2 -> 1` tail.

## Summary of Code Changed

- Added `argparse` handling with positional args `START` and `END`, plus optional `--max-steps`.
- Refactored sequence logic into modular functions: `collatz_next`, `has_421_tail`, `run_collatz_range`, `parse_args`, and `main`.
- Implemented global de-duplication output behavior to show only not-yet-calculated values.
- Added final aggregate report listing start values that did not hit `4 -> 2 -> 1`.

## Follow-up Revision

- Updated output format to only print one summary line per start value:
  - count until first `4 -> 2 -> 1` tail appearance
  - total step count for that start
- Added `number.txt` persistence behavior:
  - for each new start number, overwrite `number.txt` with that number
  - file always contains the current/last processed start value

## Threading Revision

- Added parallel sequence computation with `ThreadPoolExecutor`.
- Introduced `--workers` CLI option to control thread count.
- Kept output deterministic by printing results in numeric start order.
- Preserved `number.txt` overwrite semantics in ordered start progression so it ends on the final processed start.

## Overflow Fix Revision

- Removed eager `list(range(start, end + 1))` creation, which overflowed for very large integer ranges.
- Implemented a bounded in-flight future queue so only a small window of jobs is submitted at once.
- Kept deterministic output and `number.txt` updates in strict start-number order while still using threads for computation.
