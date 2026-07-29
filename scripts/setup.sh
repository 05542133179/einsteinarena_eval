#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${OPENARENA_PYTHON:-python3}"

"${PYTHON}" -m venv "${ROOT}/.venv"
"${ROOT}/.venv/bin/python" -m pip install --upgrade pip
"${ROOT}/.venv/bin/python" -m pip install -e "${ROOT}"

echo "Installed openarena-eval-kit in ${ROOT}/.venv"
echo "Activate with: source ${ROOT}/.venv/bin/activate"
