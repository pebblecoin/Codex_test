#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

set +e
actual="$(python3 rover.py create rover1 select rover1 create rover2 0 1 NORTH move 2>&1)"
status=$?
set -e

expected=$'create rover1: Rover rover1 created. Rover rover1: Position: (0, 0), Direction: NORTH\nselect rover1: Selected rover1. Rover rover1: Position: (0, 0), Direction: NORTH\ncreate rover2 0 1 NORTH: Rover rover2 created. Rover rover2: Position: (0, 1), Direction: NORTH\nError: Move blocked for rover1: another rover is at (0, 1).'

if [[ $status -ne 1 ]]; then
  echo "Collision CLI test failed: expected exit code 1, got $status."
  echo "Output:"
  printf '%s\n' "$actual"
  exit 1
fi

if [[ "$actual" != "$expected" ]]; then
  echo "Collision CLI test failed: output mismatch."
  echo "Expected:"
  printf '%s\n' "$expected"
  echo "Actual:"
  printf '%s\n' "$actual"
  exit 1
fi

echo "Collision CLI test passed."
