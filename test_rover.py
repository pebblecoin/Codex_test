import io
import unittest
from contextlib import redirect_stdout

from rover import CollisionError, Rover, RoverFleet, main


class RoverTests(unittest.TestCase):
    def test_initial_state(self) -> None:
        rover = Rover()

        self.assertEqual(
            rover.report(),
            "Position: (0, 0), Direction: NORTH",
        )

    def test_left_turn_reports_state(self) -> None:
        rover = Rover()

        self.assertEqual(
            rover.execute("left"),
            "Position: (0, 0), Direction: WEST",
        )

    def test_right_turn_reports_state(self) -> None:
        rover = Rover()

        self.assertEqual(
            rover.execute("right"),
            "Position: (0, 0), Direction: EAST",
        )

    def test_move_updates_position_and_reports_state(self) -> None:
        rover = Rover()

        self.assertEqual(
            rover.execute("move"),
            "Position: (0, 1), Direction: NORTH",
        )

    def test_execute_all_returns_a_report_for_each_command(self) -> None:
        rover = Rover()

        self.assertEqual(
            rover.execute_all(["move", "right", "move", "left", "move"]),
            [
                "Position: (0, 1), Direction: NORTH",
                "Position: (0, 1), Direction: EAST",
                "Position: (1, 1), Direction: EAST",
                "Position: (1, 1), Direction: NORTH",
                "Position: (1, 2), Direction: NORTH",
            ],
        )

    def test_report_command_returns_current_state(self) -> None:
        rover = Rover()

        self.assertEqual(
            rover.execute("report"),
            "Position: (0, 0), Direction: NORTH",
        )

    def test_invalid_command_raises_clear_error(self) -> None:
        rover = Rover()

        with self.assertRaises(ValueError):
            rover.execute("jump")

    def test_main_prints_reports_for_cli_commands(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main(["move", "right", "move"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            output.getvalue().splitlines(),
            [
                "move: Position: (0, 1), Direction: NORTH",
                "right: Position: (0, 1), Direction: EAST",
                "move: Position: (1, 1), Direction: EAST",
            ],
        )

    def test_main_supports_report_in_single_rover_mode(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main(["move", "report"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            output.getvalue().splitlines(),
            [
                "move: Position: (0, 1), Direction: NORTH",
                "report: Position: (0, 1), Direction: NORTH",
            ],
        )

    def test_main_without_commands_shows_usage(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            output.getvalue().splitlines(),
            [
                "Usage: python3 rover.py <command> [<command> ...]",
                "Single-rover commands: left right move report",
                "Fleet commands: create <id> [x y direction] select <id> left right move report",
            ],
        )


class RoverFleetTests(unittest.TestCase):
    def test_create_and_select_rovers(self) -> None:
        fleet = RoverFleet()

        self.assertEqual(
            fleet.create_rover("rover1"),
            "Rover rover1 created. Rover rover1: Position: (0, 0), Direction: NORTH",
        )
        self.assertEqual(
            fleet.create_rover("rover2", x=2, y=3, direction="EAST"),
            "Rover rover2 created. Rover rover2: Position: (2, 3), Direction: EAST",
        )
        self.assertEqual(
            fleet.select_rover("rover2"),
            "Selected rover2. Rover rover2: Position: (2, 3), Direction: EAST",
        )

    def test_move_selected_rover(self) -> None:
        fleet = RoverFleet()
        fleet.create_rover("rover1")
        fleet.select_rover("rover1")

        self.assertEqual(
            fleet.execute("move"),
            "Rover rover1: Position: (0, 1), Direction: NORTH",
        )

    def test_report_selected_rover(self) -> None:
        fleet = RoverFleet()
        fleet.create_rover("rover1")
        fleet.select_rover("rover1")
        fleet.execute("move")

        self.assertEqual(
            fleet.execute("report"),
            "Rover rover1: Position: (0, 1), Direction: NORTH",
        )

    def test_create_rover_rejects_occupied_position(self) -> None:
        fleet = RoverFleet()
        fleet.create_rover("rover1")

        with self.assertRaises(CollisionError):
            fleet.create_rover("rover2")

    def test_move_is_blocked_when_another_rover_occupies_target_position(self) -> None:
        fleet = RoverFleet()
        fleet.create_rover("rover1")
        fleet.create_rover("rover2", x=0, y=1, direction="EAST")
        fleet.select_rover("rover1")

        with self.assertRaises(CollisionError):
            fleet.execute("move")

    def test_execute_requires_selected_rover(self) -> None:
        fleet = RoverFleet()
        fleet.create_rover("rover1")

        with self.assertRaises(ValueError):
            fleet.execute("move")

    def test_main_supports_multi_rover_workflow(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main(
                [
                    "create",
                    "rover1",
                    "select",
                    "rover1",
                    "move",
                    "create",
                    "rover2",
                    "1",
                    "1",
                    "EAST",
                    "select",
                    "rover2",
                    "left",
                    "report",
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            output.getvalue().splitlines(),
            [
                "create rover1: Rover rover1 created. Rover rover1: Position: (0, 0), Direction: NORTH",
                "select rover1: Selected rover1. Rover rover1: Position: (0, 0), Direction: NORTH",
                "move: Rover rover1: Position: (0, 1), Direction: NORTH",
                "create rover2 1 1 EAST: Rover rover2 created. Rover rover2: Position: (1, 1), Direction: EAST",
                "select rover2: Selected rover2. Rover rover2: Position: (1, 1), Direction: EAST",
                "left: Rover rover2: Position: (1, 1), Direction: NORTH",
                "report: Rover rover2: Position: (1, 1), Direction: NORTH",
            ],
        )

    def test_main_returns_error_for_collision(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main(
                [
                    "create",
                    "rover1",
                    "select",
                    "rover1",
                    "create",
                    "rover2",
                    "0",
                    "1",
                    "NORTH",
                    "move",
                ]
            )

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            output.getvalue().splitlines(),
            [
                "create rover1: Rover rover1 created. Rover rover1: Position: (0, 0), Direction: NORTH",
                "select rover1: Selected rover1. Rover rover1: Position: (0, 0), Direction: NORTH",
                "create rover2 0 1 NORTH: Rover rover2 created. Rover rover2: Position: (0, 1), Direction: NORTH",
                "Error: Move blocked for rover1: another rover is at (0, 1).",
            ],
        )


if __name__ == "__main__":
    unittest.main()
