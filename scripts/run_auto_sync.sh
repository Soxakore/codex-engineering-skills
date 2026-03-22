#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${REPO_ROOT}/telemetry"
mkdir -p "${LOG_DIR}"

python3 "${REPO_ROOT}/scripts/sync_codex_skill_runs.py" --render >>"${LOG_DIR}/auto-sync.log" 2>&1
