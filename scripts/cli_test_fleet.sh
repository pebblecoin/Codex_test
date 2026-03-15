#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

actual="$(python3 rover.py create rover1 select rover1 move create rover2 2 2 EAST select rover2 left report)"
expected=$'create rover1: Rover rover1 created. Rover rover1: Position: (0, 0), Direction: NORTH\nselect rover1: Selected rover1. Rover rover1: Position: (0, 0), Direction: NORTH\nmove: Rover rover1: Position: (0, 1), Direction: NORTH\ncreate rover2 2 2 EAST: Rover rover2 created. Rover rover2: Position: (2, 2), Direction: EAST\nselect rover2: Selected rover2. Rover rover2: Position: (2, 2), Direction: EAST\nleft: Rover rover2: Position: (2, 2), Direction: NORTH\nreport: Rover rover2: Position: (2, 2), Direction: NORTH'

if [[ "$actual" != "$expected" ]]; then
  echo "Fleet CLI test failed."
  echo "Expected:"
  printf '%s\n' "$expected"
  echo "Actual:"
  printf '%s\n' "$actual"
  exit 1
fi

echo "Fleet CLI test passed."
