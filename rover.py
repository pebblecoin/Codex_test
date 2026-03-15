import sys
from dataclasses import dataclass


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


@dataclass
class Rover:
    x: int = 0
    y: int = 0
    direction: str = "NORTH"

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

        raise ValueError(
            f"Unknown command: {command}. Supported commands are left, right, move."
        )

    def execute_all(self, commands: list[str]) -> list[str]:
        return [self.execute(command) for command in commands]


def main(args: list[str]) -> int:
    if not args:
        print("Usage: python3 rover.py <command> [<command> ...]")
        print("Supported commands: left right move")
        return 1

    rover = Rover()

    for command in args:
        print(f"{command}: {rover.execute(command)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
