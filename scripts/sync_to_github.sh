#!/usr/bin/env bash
set -euo pipefail

MESSAGE="${1:-Update sxRaep package and PyDoc documentation}"

if [[ ! -d .git ]]; then
  echo "Error: run this script from the root of the Git repository." >&2
  exit 1
fi

python scripts/generate_pydoc.py

git status
read -r -p "Proceed with git add/commit/push? [y/N] " answer
if [[ ! "$answer" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

git add .
git commit -m "$MESSAGE" || echo "No changes to commit."
git push origin HEAD
