# Mars Rover Interview Answer Sheet

## 1) Why `stderr` for errors?
Errors should go to `stderr` so normal program output stays clean on `stdout`. This makes automation easier because scripts can separately process results and failures.

## 2) Why keep `2>&1` in shell tests?
`2>&1` keeps tests resilient by capturing both output streams. It still works if error handling later moves from `stdout` to `stderr`.

## 3) CLI parser robustness
`rover_advance.py` uses `argparse` subcommands (`create`, `select`, `move`, `tick`, etc.) instead of manual token indexing. This improves validation, help text, and maintainability.

## 4) Supporting compact commands like `MMRML`
`compact` mode translates command characters (`M`, `L`, `R`) into normal rover actions while preserving the existing explicit command style.

## 5) Simultaneous move safety
`tick` supports concurrent moves for multiple rovers and validates:
- duplicate target collisions
- swap collisions (`A -> B` while `B -> A`)
- boundary/obstacle violations

## 6) Complexity improvements
Occupancy uses a position index (`position -> rover_id`). Collision checks are `O(1)` average on create/move, rather than scanning all rovers.

## 7) Persistence strategy
Fleet state is persisted to JSON (`--state-file`) between runs, including world config, obstacles, rover states, and selected rover ID.

## 8) Observability
`--verbose` enables structured operational logs so command execution and failures are visible for debugging and production tracing.

## 9) Missing test categories addressed
Advanced tests cover invalid directions, selection errors, compact commands, obstacle/boundary rejections, and simultaneous swap collision checks.

## 10) Boundaries and obstacles
The advanced implementation introduces a `World` model that validates map bounds and obstacles before placement/movement.
