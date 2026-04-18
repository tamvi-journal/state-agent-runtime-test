#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=src

if command -v pytest >/dev/null 2>&1; then
  pytest -q
  exit $?
fi

python_cmd=""
for candidate in \
  "C:/Users/gamph/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe" \
  "./.venv/Scripts/python.exe" \
  "./.venv/bin/python"
do
  if [ -x "$candidate" ]; then
    python_cmd="$candidate"
    break
  fi
done

if [ -z "$python_cmd" ]; then
  for command_name in python3 python py; do
    if command -v "$command_name" >/dev/null 2>&1; then
      python_cmd="$command_name"
      break
    fi
  done
fi

if [ -z "$python_cmd" ]; then
  echo "Neither pytest nor a Python interpreter is available. Cannot run tests/tier_transition_smoke.py." >&2
  exit 1
fi

echo "pytest not found; running tests/tier_transition_smoke.py instead."
"$python_cmd" tests/tier_transition_smoke.py
