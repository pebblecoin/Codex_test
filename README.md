# Mars Rover Control

This project provides a simple Mars rover controller.

It supports:

- a single rover that starts at `(0, 0)` facing `NORTH`
- multiple rovers managed by a fleet controller
- `left`, `right`, `move`, and `report`
- collision prevention between rovers
- reporting position and direction after every command

## Run a single rover from the command line

```bash
python3 rover.py move right move report
```

Example output:

```text
move: Position: (0, 1), Direction: NORTH
right: Position: (0, 1), Direction: EAST
move: Position: (1, 1), Direction: EAST
report: Position: (1, 1), Direction: EAST
```

## Run multiple rovers from the command line

```bash
python3 rover.py create rover1 select rover1 move create rover2 2 2 EAST select rover2 left report
```

Example output:

```text
create rover1: Rover rover1 created. Rover rover1: Position: (0, 0), Direction: NORTH
select rover1: Selected rover1. Rover rover1: Position: (0, 0), Direction: NORTH
move: Rover rover1: Position: (0, 1), Direction: NORTH
create rover2 2 2 EAST: Rover rover2 created. Rover rover2: Position: (2, 2), Direction: EAST
select rover2: Selected rover2. Rover rover2: Position: (2, 2), Direction: EAST
left: Rover rover2: Position: (2, 2), Direction: NORTH
report: Rover rover2: Position: (2, 2), Direction: NORTH
```

## Use in code

```python
from rover import RoverFleet

fleet = RoverFleet()
print(fleet.create_rover("rover1"))
print(fleet.create_rover("rover2", x=1, y=1, direction="EAST"))
print(fleet.select_rover("rover1"))
print(fleet.execute("move"))
print(fleet.select_rover("rover2"))
print(fleet.execute("report"))
```

Example output:

```text
Rover rover1 created. Rover rover1: Position: (0, 0), Direction: NORTH
Rover rover2 created. Rover rover2: Position: (1, 1), Direction: EAST
Selected rover1. Rover rover1: Position: (0, 0), Direction: NORTH
Rover rover1: Position: (0, 1), Direction: NORTH
Selected rover2. Rover rover2: Position: (1, 1), Direction: EAST
Rover rover2: Position: (1, 1), Direction: EAST
```

## Run tests

```bash
python3 -m unittest test_rover.py
```
