#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENT_ID="com.soxakore.codex-skill-telemetry"
PLIST_DIR="${HOME}/Library/LaunchAgents"
PLIST_PATH="${PLIST_DIR}/${AGENT_ID}.plist"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3)}"

if [ -z "${PYTHON_BIN}" ]; then
  echo "python3 not found on PATH" >&2
  exit 1
fi

mkdir -p "${PLIST_DIR}" "${REPO_ROOT}/telemetry"

cat >"${PLIST_PATH}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${AGENT_ID}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${PYTHON_BIN}</string>
    <string>${REPO_ROOT}/scripts/sync_codex_skill_runs.py</string>
    <string>--render</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${REPO_ROOT}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>1800</integer>
  <key>StandardOutPath</key>
  <string>${REPO_ROOT}/telemetry/launchd.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>${REPO_ROOT}/telemetry/launchd.stderr.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)" "${PLIST_PATH}" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "${PLIST_PATH}"
launchctl kickstart -k "gui/$(id -u)/${AGENT_ID}"

echo "Installed launch agent: ${AGENT_ID}"
echo "Plist: ${PLIST_PATH}"
