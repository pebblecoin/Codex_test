import io
import unittest
from contextlib import redirect_stdout

from rover import Rover, main


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

    def test_main_without_commands_shows_usage(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            output.getvalue().splitlines(),
            [
                "Usage: python3 rover.py <command> [<command> ...]",
                "Supported commands: left right move",
            ],
        )


if __name__ == "__main__":
    unittest.main()
