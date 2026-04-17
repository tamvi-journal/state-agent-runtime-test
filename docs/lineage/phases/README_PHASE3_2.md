# Phase 3.2 — Tracey Integration Skeleton

This pack integrates Tracey core into runtime flow as a light child-layer.

## Files
- `src/tracey/tracey_adapter.py`
- `src/runtime/tracey_runtime_pass.py`
- `tests/test_tracey_integration.py`

## Goal
Let Tracey:
- inspect a turn
- detect home/build hint
- reactivate small memory items
- patch runtime state lightly
- adapt response in a bounded way

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
