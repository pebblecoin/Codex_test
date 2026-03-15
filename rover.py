import sys
from dataclasses import dataclass
from typing import Optional


LEFT_TURN = {
    "NORTH": "WEST",
    "WEST": "SOUTH",
    "SOUTH": "EAST",
    "EAST": "NORTH",
}

RIGHT_TURN = {
    "NORTH": "EAST",
    "EAST": "SOUTH",
    "SOUTH": "WEST",
    "WEST": "NORTH",
}

MOVEMENTS = {
    "NORTH": (0, 1),
    "EAST": (1, 0),
    "SOUTH": (0, -1),
    "WEST": (-1, 0),
}

SIMPLE_COMMANDS = {"left", "right", "move", "report"}
FLEET_COMMANDS = {"create", "select", *SIMPLE_COMMANDS}


class CollisionError(ValueError):
    pass


@dataclass
class Rover:
    x: int = 0
    y: int = 0
    direction: str = "NORTH"

    def __post_init__(self) -> None:
        self.direction = self.direction.upper()

        if self.direction not in MOVEMENTS:
            raise ValueError(
                f"Unknown direction: {self.direction}. "
                "Supported directions are NORTH, EAST, SOUTH, WEST."
            )

    def left(self) -> str:
        self.direction = LEFT_TURN[self.direction]
        return self.report()

    def right(self) -> str:
        self.direction = RIGHT_TURN[self.direction]
        return self.report()

    def move(self) -> str:
        dx, dy = MOVEMENTS[self.direction]
        self.x += dx
        self.y += dy
        return self.report()

    def next_position(self) -> tuple[int, int]:
        dx, dy = MOVEMENTS[self.direction]
        return self.x + dx, self.y + dy

    def report(self) -> str:
        return f"Position: ({self.x}, {self.y}), Direction: {self.direction}"

    def execute(self, command: str) -> str:
        normalized = command.strip().lower()

        if normalized == "left":
            return self.left()
        if normalized == "right":
            return self.right()
        if normalized == "move":
            return self.move()
        if normalized == "report":
            return self.report()

        raise ValueError(
            "Unknown command: "
            f"{command}. Supported commands are left, right, move, report."
        )

    def execute_all(self, commands: list[str]) -> list[str]:
        return [self.execute(command) for command in commands]


@dataclass
class RoverFleet:
    rovers: dict[str, Rover]
    position_to_rover: dict[tuple[int, int], str]
    selected_rover_id: Optional[str] = None

    def __init__(self) -> None:
        self.rovers = {}
        self.position_to_rover = {}
        self.selected_rover_id = None

    def create_rover(
        self,
        rover_id: str,
        x: int = 0,
        y: int = 0,
        direction: str = "NORTH",
    ) -> str:
        if rover_id in self.rovers:
            raise ValueError(f"Rover {rover_id} already exists.")

        if (x, y) in self.position_to_rover:
            raise CollisionError(
                f"Cannot place rover {rover_id} at ({x}, {y}) because the position is occupied."
            )

        rover = Rover(x=x, y=y, direction=direction)
        self.rovers[rover_id] = rover
        self.position_to_rover[(x, y)] = rover_id
        return f"Rover {rover_id} created. {self.describe_rover(rover_id)}"

    def select_rover(self, rover_id: str) -> str:
        if rover_id not in self.rovers:
            raise ValueError(f"Rover {rover_id} does not exist.")

        self.selected_rover_id = rover_id
        return f"Selected {rover_id}. {self.describe_rover(rover_id)}"

    def execute(self, command: str) -> str:
        rover_id = self.require_selected_rover_id()
        rover = self.rovers[rover_id]
        normalized = command.strip().lower()

        if normalized == "move":
            previous_position = (rover.x, rover.y)
            next_position = rover.next_position()
            occupying_rover_id = self.position_to_rover.get(next_position)

            if occupying_rover_id is not None and occupying_rover_id != rover_id:
                raise CollisionError(
                    f"Move blocked for {rover_id}: another rover is at {next_position}."
                )

            rover.execute(normalized)
            del self.position_to_rover[previous_position]
            self.position_to_rover[(rover.x, rover.y)] = rover_id
            return self.describe_rover(rover_id)

        rover.execute(normalized)
        return self.describe_rover(rover_id)

    def require_selected_rover_id(self) -> str:
        if self.selected_rover_id is None:
            raise ValueError("No rover selected. Use select <rover_id> first.")

        return self.selected_rover_id

    def occupied_positions(self, exclude_rover_id: Optional[str] = None) -> set[tuple[int, int]]:
        if exclude_rover_id is None:
            return set(self.position_to_rover)

        return {
            position
            for position, rover_id in self.position_to_rover.items()
            if rover_id != exclude_rover_id
        }

    def describe_rover(self, rover_id: str) -> str:
        return f"Rover {rover_id}: {self.rovers[rover_id].report()}"


def run_single_rover_cli(args: list[str]) -> int:
    rover = Rover()

    for command in args:
        print(f"{command}: {rover.execute(command)}")

    return 0


def run_fleet_cli(args: list[str]) -> int:
    fleet = RoverFleet()
    index = 0

    while index < len(args):
        command = args[index].lower()

        if command == "create":
            if index + 1 >= len(args):
                raise ValueError("create requires a rover ID.")

            rover_id = args[index + 1]
            x = 0
            y = 0
            direction = "NORTH"
            consumed = 2

            if (
                index + 4 < len(args)
                and is_int(args[index + 2])
                and is_int(args[index + 3])
                and args[index + 4].upper() in MOVEMENTS
            ):
                x = int(args[index + 2])
                y = int(args[index + 3])
                direction = args[index + 4]
                consumed = 5

            print(f"{' '.join(args[index:index + consumed])}: {fleet.create_rover(rover_id, x, y, direction)}")
            index += consumed
            continue

        if command == "select":
            if index + 1 >= len(args):
                raise ValueError("select requires a rover ID.")

            rover_id = args[index + 1]
            print(f"select {rover_id}: {fleet.select_rover(rover_id)}")
            index += 2
            continue

        if command in SIMPLE_COMMANDS:
            print(f"{command}: {fleet.execute(command)}")
            index += 1
            continue

        raise ValueError(
            "Unknown command: "
            f"{args[index]}. Supported commands are create, select, left, right, move, report."
        )

    return 0


def is_int(value: str) -> bool:
    try:
        int(value)
    except ValueError:
        return False

    return True


def main(args: list[str]) -> int:
    if not args:
        print("Usage: python3 rover.py <command> [<command> ...]")
        print("Single-rover commands: left right move report")
        print(
            "Fleet commands: create <id> [x y direction] select <id> left right move report"
        )
        return 1

    try:
        if all(command.lower() in SIMPLE_COMMANDS for command in args):
            return run_single_rover_cli(args)

        return run_fleet_cli(args)
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
