#!/usr/bin/env bash
# Print the newest Flame-bundled python3 under /opt/Autodesk/python.
# Usage: "$(./tools/find_flame_python.sh)" tools/bootstrap_from_channel.py --channel dev
set -euo pipefail

BASE="${FLAME_PYTHON_ROOT:-/opt/Autodesk/python}"
if [[ ! -d "$BASE" ]]; then
  echo "Embr: no directory $BASE" >&2
  exit 1
fi

# Prefer explicit override.
if [[ -n "${FLAME_PYTHON:-}" && -x "${FLAME_PYTHON}" ]]; then
  echo "$FLAME_PYTHON"
  exit 0
fi

newest=""
# sort -V: 2025.2.7 > 2025.2.6 > 2024.2.3
while IFS= read -r dir; do
  cand="$dir/bin/python3"
  if [[ -x "$cand" ]]; then
    newest="$cand"
  fi
done < <(ls -1d "$BASE"/[0-9]* 2>/dev/null | sort -V)

if [[ -z "$newest" ]]; then
  echo "Embr: no …/bin/python3 under $BASE (looked for versioned folders like 2025.2.7)" >&2
  exit 1
fi

echo "$newest"
