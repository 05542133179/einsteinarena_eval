#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ -n "${OPENARENA_PYTHON:-}" ]; then
  PYTHON="${OPENARENA_PYTHON}"
elif [ -x "${PROJECT_ROOT}/.venv/bin/python" ]; then
  PYTHON="${PROJECT_ROOT}/.venv/bin/python"
else
  PYTHON="python3"
fi

cd "${PROJECT_ROOT}"
exec "${PYTHON}" -m openarena_eval "$@"
