#!/usr/bin/env bash
# Demo: run the full test suite (includes fixture-based demo test).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PY="${ROOT}/.venv/bin/python"
else
  PY="${PYTHON:-python3}"
fi

echo "[INFO]: repo root: ${ROOT}"
echo "[INFO]: python: ${PY} ($("${PY}" -V 2>&1))"
echo "[INFO]: running pytest tests/ ..."
"${PY}" -m pytest -q tests/
echo "[INFO]: done."
