#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

actual="$(python3 rover.py move right move report)"
expected=$'move: Position: (0, 1), Direction: NORTH\nright: Position: (0, 1), Direction: EAST\nmove: Position: (1, 1), Direction: EAST\nreport: Position: (1, 1), Direction: EAST'

if [[ "$actual" != "$expected" ]]; then
  echo "Single rover CLI test failed."
  echo "Expected:"
  printf '%s\n' "$expected"
  echo "Actual:"
  printf '%s\n' "$actual"
  exit 1
fi

echo "Single rover CLI test passed."
