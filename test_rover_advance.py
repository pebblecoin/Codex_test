import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from rover_advance import main


class RoverAdvanceTests(unittest.TestCase):
    def run_cli(self, argv: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(argv)
        return exit_code, stdout.getvalue().strip(), stderr.getvalue().strip()

    def test_persisted_single_rover_flow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = str(Path(temp_dir) / "state.json")

            self.assertEqual(
                self.run_cli(["--state-file", state_file, "init", "--width", "5", "--height", "5"])[0],
                0,
            )
            self.assertEqual(
                self.run_cli(
                    [
                        "--state-file",
                        state_file,
                        "create",
                        "rover1",
                        "--x",
                        "1",
                        "--y",
                        "1",
                        "--direction",
                        "NORTH",
                    ]
                )[0],
                0,
            )
            self.assertEqual(
                self.run_cli(["--state-file", state_file, "select", "rover1"])[0], 0
            )
            self.assertEqual(
                self.run_cli(["--state-file", state_file, "move"])[1],
                "Rover rover1: Position: (1, 2), Direction: NORTH",
            )
            self.assertEqual(
                self.run_cli(["--state-file", state_file, "report"])[1],
                "Rover rover1: Position: (1, 2), Direction: NORTH",
            )

    def test_errors_go_to_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = str(Path(temp_dir) / "state.json")
            self.run_cli(["--state-file", state_file, "init"])

            exit_code, stdout, stderr = self.run_cli(
                ["--state-file", state_file, "move"]
            )

            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertIn("Error: No rover selected.", stderr)

    def test_compact_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = str(Path(temp_dir) / "state.json")
            self.run_cli(["--state-file", state_file, "init"])
            self.run_cli(["--state-file", state_file, "create", "rover1"])
            self.run_cli(["--state-file", state_file, "select", "rover1"])

            exit_code, stdout, _ = self.run_cli(
                ["--state-file", state_file, "compact", "MMRML"]
            )

            self.assertEqual(exit_code, 0)
            self.assertIn("Rover rover1: Position: (1, 2), Direction: NORTH", stdout)

    def test_tick_swap_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = str(Path(temp_dir) / "state.json")
            self.run_cli(["--state-file", state_file, "init"])
            self.run_cli(
                [
                    "--state-file",
                    state_file,
                    "create",
                    "rover1",
                    "--x",
                    "0",
                    "--y",
                    "0",
                    "--direction",
                    "EAST",
                ]
            )
            self.run_cli(
                [
                    "--state-file",
                    state_file,
                    "create",
                    "rover2",
                    "--x",
                    "1",
                    "--y",
                    "0",
                    "--direction",
                    "WEST",
                ]
            )

            exit_code, _, stderr = self.run_cli(
                ["--state-file", state_file, "tick", "--move", "rover1", "--move", "rover2"]
            )
            self.assertEqual(exit_code, 1)
            self.assertIn("Error: Tick swap collision", stderr)

    def test_obstacle_and_boundary_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = str(Path(temp_dir) / "state.json")
            self.run_cli(
                [
                    "--state-file",
                    state_file,
                    "init",
                    "--width",
                    "2",
                    "--height",
                    "2",
                    "--obstacle",
                    "1,0",
                ]
            )
            self.run_cli(
                [
                    "--state-file",
                    state_file,
                    "create",
                    "rover1",
                    "--direction",
                    "EAST",
                ]
            )
            self.run_cli(["--state-file", state_file, "select", "rover1"])

            exit_code, _, stderr = self.run_cli(
                ["--state-file", state_file, "move"]
            )
            self.assertEqual(exit_code, 1)
            self.assertIn("Error: Position (1, 0) is out of bounds or blocked", stderr)


if __name__ == "__main__":
    unittest.main()
