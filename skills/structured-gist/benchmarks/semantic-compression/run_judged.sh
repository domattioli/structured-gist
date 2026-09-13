#!/usr/bin/env bash
# Judged (model-dependent) semantic-compression scoring lane.
# Invokes a judge to score semantic preservation across compression levels.
# Requires model access and is NOT run in CI/deterministic workflows.
#
# Exit code: 0 = success, 2 = unavailable (no judged result available), other = failure.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "FATAL: not in a git repo"
  exit 1
}

cd "$SCRIPT_DIR" || exit 1

python3 run.py --lane judged
exit $?
