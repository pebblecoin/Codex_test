import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
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

COMPACT_MAP = {"M": "move", "L": "left", "R": "right"}

LOG = logging.getLogger("rover_advance")


class RoverError(ValueError):
    pass


class CollisionError(RoverError):
    pass


class ValidationError(RoverError):
    pass


@dataclass
class Rover:
    x: int = 0
    y: int = 0
    direction: str = "NORTH"

    def __post_init__(self) -> None:
        self.direction = self.direction.upper()
        if self.direction not in MOVEMENTS:
            raise ValidationError(
                f"Unknown direction: {self.direction}. "
                "Supported directions are NORTH, EAST, SOUTH, WEST."
            )

    def next_position(self) -> tuple[int, int]:
        dx, dy = MOVEMENTS[self.direction]
        return self.x + dx, self.y + dy

    def turn_left(self) -> None:
        self.direction = LEFT_TURN[self.direction]

    def turn_right(self) -> None:
        self.direction = RIGHT_TURN[self.direction]

    def report(self) -> str:
        return f"Position: ({self.x}, {self.y}), Direction: {self.direction}"


@dataclass
class World:
    width: Optional[int] = None
    height: Optional[int] = None
    obstacles: set[tuple[int, int]] = field(default_factory=set)

    def is_in_bounds(self, position: tuple[int, int]) -> bool:
        x, y = position
        if self.width is not None and not (0 <= x < self.width):
            return False
        if self.height is not None and not (0 <= y < self.height):
            return False
        return True

    def is_blocked(self, position: tuple[int, int]) -> bool:
        return (not self.is_in_bounds(position)) or (position in self.obstacles)


class RoverFleet:
    def __init__(self, world: Optional[World] = None) -> None:
        self.world = world if world is not None else World()
        self.rovers: dict[str, Rover] = {}
        self.position_to_rover: dict[tuple[int, int], str] = {}
        self.selected_rover_id: Optional[str] = None

    def create_rover(
        self,
        rover_id: str,
        x: int = 0,
        y: int = 0,
        direction: str = "NORTH",
    ) -> str:
        if rover_id in self.rovers:
            raise ValidationError(f"Rover {rover_id} already exists.")

        rover = Rover(x=x, y=y, direction=direction)
        position = (rover.x, rover.y)
        self._ensure_position_available(position)
        self.rovers[rover_id] = rover
        self.position_to_rover[position] = rover_id
        LOG.info(
            "event=create rover_id=%s x=%s y=%s direction=%s",
            rover_id,
            rover.x,
            rover.y,
            rover.direction,
        )
        return f"Rover {rover_id}: {rover.report()}"

    def select_rover(self, rover_id: str) -> str:
        if rover_id not in self.rovers:
            raise ValidationError(f"Rover {rover_id} does not exist.")
        self.selected_rover_id = rover_id
        LOG.info("event=select rover_id=%s", rover_id)
        return f"Selected {rover_id}. {self.describe_rover(rover_id)}"

    def list_rovers(self) -> list[str]:
        return [self.describe_rover(rover_id) for rover_id in sorted(self.rovers)]

    def add_obstacle(self, position: tuple[int, int]) -> str:
        if not self.world.is_in_bounds(position):
            raise ValidationError(f"Obstacle {position} is out of world bounds.")
        if position in self.position_to_rover:
            raise CollisionError(
                f"Cannot add obstacle at {position} because rover {self.position_to_rover[position]} is there."
            )
        self.world.obstacles.add(position)
        LOG.info("event=add_obstacle position=%s", position)
        return f"Obstacle added at {position}."

    def execute_selected(self, command: str) -> str:
        rover_id = self.require_selected_rover_id()
        return self.execute_for_rover(rover_id, command)

    def execute_for_rover(self, rover_id: str, command: str) -> str:
        if rover_id not in self.rovers:
            raise ValidationError(f"Rover {rover_id} does not exist.")

        rover = self.rovers[rover_id]
        normalized = command.lower().strip()

        if normalized == "left":
            rover.turn_left()
        elif normalized == "right":
            rover.turn_right()
        elif normalized == "move":
            next_position = rover.next_position()
            self._ensure_position_available(next_position, ignore_rover_id=rover_id)
            self._move_rover(rover_id, next_position)
        elif normalized == "report":
            pass
        else:
            raise ValidationError(
                f"Unknown command: {command}. Supported commands are left, right, move, report."
            )

        LOG.info("event=execute rover_id=%s command=%s", rover_id, normalized)
        return self.describe_rover(rover_id)

    def execute_compact(self, compact_commands: str, rover_id: Optional[str] = None) -> list[str]:
        target_id = rover_id if rover_id is not None else self.require_selected_rover_id()
        reports: list[str] = []
        for token in compact_commands.upper():
            if token.isspace():
                continue
            if token not in COMPACT_MAP:
                raise ValidationError(
                    f"Unknown compact command: {token}. Supported compact commands are M, L, R."
                )
            reports.append(self.execute_for_rover(target_id, COMPACT_MAP[token]))
        return reports

    def tick(self, move_rover_ids: list[str]) -> list[str]:
        if not move_rover_ids:
            raise ValidationError("tick requires at least one --move rover_id.")

        move_set = set(move_rover_ids)
        if len(move_set) != len(move_rover_ids):
            raise ValidationError("tick received duplicate rover IDs.")

        for rover_id in move_set:
            if rover_id not in self.rovers:
                raise ValidationError(f"Rover {rover_id} does not exist.")

        current_positions = {
            rover_id: (rover.x, rover.y) for rover_id, rover in self.rovers.items()
        }
        target_positions = dict(current_positions)

        for rover_id in move_set:
            next_position = self.rovers[rover_id].next_position()
            if self.world.is_blocked(next_position):
                raise ValidationError(
                    f"Tick blocked for {rover_id}: target {next_position} is out of bounds or an obstacle."
                )
            target_positions[rover_id] = next_position

        position_to_ids: dict[tuple[int, int], list[str]] = {}
        for rover_id, target_position in target_positions.items():
            position_to_ids.setdefault(target_position, []).append(rover_id)

        collisions = [
            (position, rover_ids)
            for position, rover_ids in position_to_ids.items()
            if len(rover_ids) > 1
        ]
        if collisions:
            position, rover_ids = collisions[0]
            rover_ids.sort()
            raise CollisionError(
                f"Tick collision at {position}: rovers {', '.join(rover_ids)} target the same cell."
            )

        move_list = sorted(move_set)
        for index, rover_a in enumerate(move_list):
            for rover_b in move_list[index + 1 :]:
                if (
                    target_positions[rover_a] == current_positions[rover_b]
                    and target_positions[rover_b] == current_positions[rover_a]
                    and current_positions[rover_a] != current_positions[rover_b]
                ):
                    raise CollisionError(
                        f"Tick swap collision between {rover_a} and {rover_b}."
                    )

        for rover_id, target in target_positions.items():
            self.rovers[rover_id].x = target[0]
            self.rovers[rover_id].y = target[1]

        self.position_to_rover = {
            (rover.x, rover.y): rover_id for rover_id, rover in self.rovers.items()
        }
        LOG.info("event=tick moves=%s", ",".join(sorted(move_set)))
        return [self.describe_rover(rover_id) for rover_id in sorted(self.rovers)]

    def require_selected_rover_id(self) -> str:
        if self.selected_rover_id is None:
            raise ValidationError("No rover selected. Use select <rover_id> first.")
        return self.selected_rover_id

    def describe_rover(self, rover_id: str) -> str:
        rover = self.rovers[rover_id]
        return f"Rover {rover_id}: {rover.report()}"

    def _ensure_position_available(
        self,
        position: tuple[int, int],
        ignore_rover_id: Optional[str] = None,
    ) -> None:
        if self.world.is_blocked(position):
            raise ValidationError(
                f"Position {position} is out of bounds or blocked by an obstacle."
            )

        occupant = self.position_to_rover.get(position)
        if occupant is not None and occupant != ignore_rover_id:
            raise CollisionError(
                f"Position {position} is occupied by rover {occupant}."
            )

    def _move_rover(self, rover_id: str, position: tuple[int, int]) -> None:
        rover = self.rovers[rover_id]
        old_position = (rover.x, rover.y)
        rover.x, rover.y = position
        del self.position_to_rover[old_position]
        self.position_to_rover[position] = rover_id

    def to_dict(self) -> dict:
        return {
            "world": {
                "width": self.world.width,
                "height": self.world.height,
                "obstacles": [list(position) for position in sorted(self.world.obstacles)],
            },
            "selected_rover_id": self.selected_rover_id,
            "rovers": [
                {
                    "id": rover_id,
                    "x": rover.x,
                    "y": rover.y,
                    "direction": rover.direction,
                }
                for rover_id, rover in sorted(self.rovers.items())
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RoverFleet":
        world_data = data.get("world", {})
        obstacles = {
            (int(position[0]), int(position[1]))
            for position in world_data.get("obstacles", [])
        }
        world = World(
            width=world_data.get("width"),
            height=world_data.get("height"),
            obstacles=obstacles,
        )
        fleet = cls(world=world)
        for rover_data in data.get("rovers", []):
            fleet.create_rover(
                rover_data["id"],
                x=int(rover_data["x"]),
                y=int(rover_data["y"]),
                direction=str(rover_data["direction"]),
            )
        selected = data.get("selected_rover_id")
        if selected is not None:
            fleet.select_rover(str(selected))
        return fleet

    def save_state(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_state(cls, path: Path) -> "RoverFleet":
        if not path.exists():
            return cls()
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))


def parse_position(raw_value: str) -> tuple[int, int]:
    parts = raw_value.split(",")
    if len(parts) != 2:
        raise ValidationError(f"Invalid position {raw_value}. Use x,y format.")
    try:
        return int(parts[0]), int(parts[1])
    except ValueError as error:
        raise ValidationError(f"Invalid numeric position {raw_value}.") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Advanced Mars rover controller with persistence and safe multi-rover operations."
    )
    parser.add_argument(
        "--state-file",
        default="rover_advanced_state.json",
        help="Path to JSON state file used between commands.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose operational logs.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize or reset fleet state.")
    init_parser.add_argument("--width", type=int, default=None)
    init_parser.add_argument("--height", type=int, default=None)
    init_parser.add_argument(
        "--obstacle",
        action="append",
        default=[],
        help="Obstacle position in x,y format. Can be repeated.",
    )

    create_parser = subparsers.add_parser("create", help="Create a rover.")
    create_parser.add_argument("rover_id")
    create_parser.add_argument("--x", type=int, default=0)
    create_parser.add_argument("--y", type=int, default=0)
    create_parser.add_argument("--direction", default="NORTH")

    select_parser = subparsers.add_parser("select", help="Select an active rover.")
    select_parser.add_argument("rover_id")

    subparsers.add_parser("left", help="Turn selected rover left.")
    subparsers.add_parser("right", help="Turn selected rover right.")
    subparsers.add_parser("move", help="Move selected rover forward.")
    subparsers.add_parser("report", help="Report selected rover state.")
    subparsers.add_parser("list", help="List all rover states.")

    compact_parser = subparsers.add_parser(
        "compact",
        help="Run compact command string (M/L/R) for a rover.",
    )
    compact_parser.add_argument("commands")
    compact_parser.add_argument("--rover", default=None)

    tick_parser = subparsers.add_parser(
        "tick",
        help="Move multiple rovers simultaneously by one step.",
    )
    tick_parser.add_argument(
        "--move",
        dest="moves",
        action="append",
        default=[],
        help="Rover ID to move forward in this tick. Can be repeated.",
    )

    obstacle_parser = subparsers.add_parser(
        "add-obstacle", help="Add an obstacle to the world."
    )
    obstacle_parser.add_argument("position", help="Position in x,y format.")

    return parser


def configure_logging(verbose: bool) -> None:
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


def load_or_init_fleet_for_command(
    command: str,
    state_path: Path,
    width: Optional[int],
    height: Optional[int],
    obstacles: list[str],
) -> RoverFleet:
    if command != "init":
        return RoverFleet.load_state(state_path)

    world = World(width=width, height=height)
    for raw_position in obstacles:
        world.obstacles.add(parse_position(raw_position))
    return RoverFleet(world=world)


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)
    state_path = Path(args.state_file)

    try:
        fleet = load_or_init_fleet_for_command(
            command=args.command,
            state_path=state_path,
            width=getattr(args, "width", None),
            height=getattr(args, "height", None),
            obstacles=getattr(args, "obstacle", []),
        )

        if args.command == "init":
            fleet.save_state(state_path)
            print(
                f"Initialized state at {state_path} with "
                f"width={fleet.world.width}, height={fleet.world.height}, "
                f"obstacles={sorted(fleet.world.obstacles)}."
            )
            return 0

        if args.command == "create":
            message = fleet.create_rover(
                rover_id=args.rover_id,
                x=args.x,
                y=args.y,
                direction=args.direction,
            )
            fleet.save_state(state_path)
            print(message)
            return 0

        if args.command == "select":
            message = fleet.select_rover(args.rover_id)
            fleet.save_state(state_path)
            print(message)
            return 0

        if args.command in {"left", "right", "move", "report"}:
            message = fleet.execute_selected(args.command)
            fleet.save_state(state_path)
            print(message)
            return 0

        if args.command == "compact":
            reports = fleet.execute_compact(args.commands, rover_id=args.rover)
            fleet.save_state(state_path)
            for report in reports:
                print(report)
            return 0

        if args.command == "tick":
            reports = fleet.tick(args.moves)
            fleet.save_state(state_path)
            for report in reports:
                print(report)
            return 0

        if args.command == "add-obstacle":
            message = fleet.add_obstacle(parse_position(args.position))
            fleet.save_state(state_path)
            print(message)
            return 0

        if args.command == "list":
            for report in fleet.list_rovers():
                print(report)
            return 0

        raise ValidationError(f"Unsupported command: {args.command}")
    except (RoverError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
