#!/usr/bin/env bash
# Deterministic (model-free) semantic-compression scoring lane.
# Runs suite.json cases, produces results/deterministic.json.
# Does NOT call any model. Requires source.md + gold.json only.
#
# Exit code: 0 = success, 1 = failure.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "FATAL: not in a git repo"
  exit 1
}

cd "$SCRIPT_DIR" || exit 1

python3 run.py --lane deterministic
exit $?
