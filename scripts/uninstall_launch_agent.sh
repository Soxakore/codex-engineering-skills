#!/usr/bin/env bash
set -euo pipefail

AGENT_ID="com.soxakore.codex-skill-telemetry"
PLIST_PATH="${HOME}/Library/LaunchAgents/${AGENT_ID}.plist"

launchctl bootout "gui/$(id -u)" "${PLIST_PATH}" >/dev/null 2>&1 || true
rm -f "${PLIST_PATH}"

echo "Removed launch agent: ${AGENT_ID}"
