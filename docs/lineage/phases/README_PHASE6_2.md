# Phase 6.2 — Shell Runtime Bridge + Operator Console Skeleton

This pack extends the external shell layer with:
- a shell-to-runtime bridge
- an operator console session object
- a shell response formatter

## Files
- `src/shell/shell_runtime_bridge.py`
- `src/shell/operator_console_session.py`
- `src/shell/shell_response_formatter.py`
- `tests/test_shell_runtime_bridge.py`

## Goal
Move from:
- shell boundary only

to:
- shell boundary + runtime handoff + operator-side inspection snapshot

This is still not a Telegram/webhook adapter.
It is the internal bridge layer before channel-specific integrations.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
