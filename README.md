# Mars Rover Control

This project provides a simple Mars rover controller.

The rover:

- starts at `(0, 0)`
- faces `NORTH`
- supports `left`, `right`, and `move`
- reports its position and direction after every command

## Run from the command line

```bash
python3 rover.py move right move
```

Example output:

```text
move: Position: (0, 1), Direction: NORTH
right: Position: (0, 1), Direction: EAST
move: Position: (1, 1), Direction: EAST
```

## Use in code

```python
from rover import Rover

rover = Rover()
commands = ["move", "right", "move"]
reports = rover.execute_all(commands)

for report in reports:
    print(report)
```

## Run tests

```bash
python3 -m unittest test_rover.py
```
