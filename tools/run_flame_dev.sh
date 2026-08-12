#!/usr/bin/env bash
# Launch Flame with this repo's scripts/ on DL_PYTHON_HOOK_PATH.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="${ROOT}/scripts"

export DL_PYTHON_HOOK_PATH="${SCRIPTS}${DL_PYTHON_HOOK_PATH:+:${DL_PYTHON_HOOK_PATH}}"

echo "DL_PYTHON_HOOK_PATH=${DL_PYTHON_HOOK_PATH}"

# Prefer versioned family launcher; fall back to flame_2025.
if [[ -x /opt/Autodesk/.flamefamily_2025/bin/startApplication ]]; then
  exec /opt/Autodesk/.flamefamily_2025/bin/startApplication "$@"
elif [[ -x /opt/Autodesk/flame_2025/bin/startApplication ]]; then
  exec /opt/Autodesk/flame_2025/bin/startApplication "$@"
else
  echo "Flame 2025 startApplication not found under /opt/Autodesk" >&2
  exit 1
fi
