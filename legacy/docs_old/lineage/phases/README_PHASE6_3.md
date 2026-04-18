# Phase 6.3 — Operator Console Dashboard Wiring

This pack wires operator-facing console views to the existing dashboard and runtime artifacts.

## Files
- `src/shell/operator_console_bridge.py`
- `src/shell/operator_console_renderer.py`
- `src/shell/operator_console_runtime.py`
- `tests/test_operator_console_dashboard_wiring.py`

## Goal
Move from:
- shell runtime bridge
- operator snapshot
- dashboard snapshot

to:
- a compact operator console payload and rendered operator text

This still stays internal.
It is the step before channel-specific adapters like Telegram.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
