# Phase 6.0 — External Shell Skeleton

This pack adds the first external shell layer around the runtime.

## Files
- `src/shell/shell_contract.py`
- `src/shell/shell_policy.py`
- `src/shell/external_shell.py`
- `src/shell/operator_snapshot.py`
- `tests/test_external_shell.py`

## Goal
Provide:
- a shell request/response contract
- render/trace/operator visibility policy
- a thin external shell wrapper
- an operator-side snapshot

This is not yet a Telegram integration.
It is the first shell boundary object.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
