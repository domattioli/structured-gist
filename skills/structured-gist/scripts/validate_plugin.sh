#!/usr/bin/env bash
# Validate plugin structure: manifest + symlink layout + dereferenced copy.
# Verifies that both symlinked and fully-dereferenced plugin layouts pass claude plugin validate.
# Also checks version consistency between SKILL.md and plugin.json.

set -euo pipefail

# Resolve repo root from script location (skills/structured-gist/scripts/validate_plugin.sh)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../" && pwd)"
cd "$REPO_ROOT" || exit 2

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

die() {
  echo "FAIL: $1" >&2
  exit 1
}

# Extract version from SKILL.md frontmatter
extract_skill_version() {
  grep "^version:" skills/structured-gist/SKILL.md | head -1 | sed 's/^version: *//;s/"//g' | xargs
}

# Extract version from plugin.json
extract_plugin_version() {
  python3 -c "import json; print(json.load(open('plugins/structured-gist/.claude-plugin/plugin.json'))['version'])" 2>/dev/null
}

# ---------------------------------------------------------------------------
# Check CLI availability
# ---------------------------------------------------------------------------
if ! command -v claude &>/dev/null; then
  echo "SKIP: claude CLI not found"
  exit 0
fi

# ---------------------------------------------------------------------------
# Step 1: Validate marketplace manifest (repo root)
# ---------------------------------------------------------------------------
echo "step 1: claude plugin validate \"\$ROOT\""
if ! claude plugin validate "$REPO_ROOT" > /dev/null 2>&1; then
  die "marketplace manifest validation failed"
fi

# ---------------------------------------------------------------------------
# Step 2: Validate symlinked layout (as shipped, symlink warning tolerated)
# ---------------------------------------------------------------------------
echo "step 2: claude plugin validate \"\$ROOT/plugins/structured-gist\" (symlinked layout)"
if ! claude plugin validate "$REPO_ROOT/plugins/structured-gist" > /dev/null 2>&1; then
  die "symlinked layout validation failed"
fi
echo "  (symlink warning tolerated)"

# ---------------------------------------------------------------------------
# Step 3: Validate dereferenced copy (must pass, no warnings)
# ---------------------------------------------------------------------------
echo "step 3: cp -RL to tmpdir, validate dereferenced copy"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

cp -RL "$REPO_ROOT/plugins/structured-gist" "$TMP_DIR/structured-gist"

VALIDATE_OUT=$(claude plugin validate "$TMP_DIR/structured-gist" 2>&1) || {
  die "dereferenced copy validation failed"
}

if echo "$VALIDATE_OUT" | grep -qi "warning"; then
  die "dereferenced copy has warnings: $(echo "$VALIDATE_OUT" | grep -i warning)"
fi

# ---------------------------------------------------------------------------
# Step 4: Assert version agreement (SKILL.md == plugin.json)
# ---------------------------------------------------------------------------
echo "step 4: version agreement check"
SKILL_VER=$(extract_skill_version)
PLUGIN_VER=$(extract_plugin_version)

if [ "$SKILL_VER" != "$PLUGIN_VER" ]; then
  die "version mismatch: SKILL.md=$SKILL_VER, plugin.json=$PLUGIN_VER"
fi

# ---------------------------------------------------------------------------
# Success
# ---------------------------------------------------------------------------
echo "validate_plugin: OK ($SKILL_VER)"
exit 0
