#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/skills"
DEST_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"

mkdir -p "$DEST_ROOT"

for skill_dir in "$SRC_DIR"/*; do
  [ -d "$skill_dir" ] || continue
  skill_name="$(basename "$skill_dir")"
  dest_dir="$DEST_ROOT/$skill_name"
  rm -rf "$dest_dir"
  cp -R "$skill_dir" "$dest_dir"
  echo "Installed $skill_name -> $dest_dir"
done

echo "Done."
