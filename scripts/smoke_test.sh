#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

"${SCRIPT_DIR}/_python.sh" validate
"${SCRIPT_DIR}/_python.sh" score \
  --slug difference-bases \
  --candidate "${PROJECT_ROOT}/examples/difference-bases.json"

if [ -n "${OPENARENA_PYTHON:-}" ]; then
  PYTHON="${OPENARENA_PYTHON}"
elif [ -x "${PROJECT_ROOT}/.venv/bin/python" ]; then
  PYTHON="${PROJECT_ROOT}/.venv/bin/python"
else
  PYTHON="python3"
fi

cd "${PROJECT_ROOT}"
"${PYTHON}" -m unittest discover -s tests -v
