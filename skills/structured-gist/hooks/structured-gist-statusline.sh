#!/bin/bash
# structured-gist-statusline.sh — Render structured-gist status for Claude Code statusLine config.
# Outputs single line (no trailing newline): [structured-gist:vX.Y.Z] or [structured-gist:active].
# Purpose: Hook script to display skill version in Claude Code prompt status bar. # Resolve script directory (works regardless of cwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_MD="${SCRIPT_DIR}/../SKILL.md" # Parse version from SKILL.md frontmatter line matching ^version:
VER=""
if [[ -f "$SKILL_MD" ]]; then VER=$(grep -E '^version:' "$SKILL_MD" | sed -E 's/^version:\s*"?([^"]+)"?.*/\1/')
fi # Output status line (no trailing newline)
if [[ -n "$VER" ]]; then printf '[structured-gist:v%s]' "$VER"
else printf '[structured-gist:active]'
fi
