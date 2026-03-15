#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

./cli_test_single.sh
./cli_test_fleet.sh
./cli_test_collision.sh

echo "All CLI tests passed."
