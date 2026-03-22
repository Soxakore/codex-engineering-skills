#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALIDATOR="${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py"

if [ ! -f "$VALIDATOR" ]; then
  echo "Validator not found at: $VALIDATOR" >&2
  echo "Expected a local Codex install with the skill creator validator available." >&2
  exit 1
fi

status=0

for skill_dir in "$REPO_ROOT"/skills/*; do
  [ -d "$skill_dir" ] || continue
  echo "Validating $(basename "$skill_dir")"
  if ! python3 "$VALIDATOR" "$skill_dir"; then
    status=1
  fi
done

exit "$status"
