# Phase 2.5 — Monitor Layer Skeleton

This package adds a small rule-based monitor.

## Files
- `src/monitor/monitor_schema.py`
- `src/monitor/monitor_layer.py`
- `tests/test_monitor_layer.py`

## Goal
Detect:
- drift
- ambiguity
- policy pressure
- fake progress
- archive overreach
- mode decay

and return:
- compact scores
- one primary recommended intervention

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
