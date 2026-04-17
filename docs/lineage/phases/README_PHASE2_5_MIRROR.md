# Phase 2.5 — Mirror Bridge Skeleton

This package adds a compact bridge between monitor output and model-visible state.

## Files
- `src/monitor/mirror_bridge.py`
- `tests/test_mirror_bridge.py`

## Purpose
- select one primary current risk
- compress monitor output into `monitor_summary`
- optionally annotate state lightly with:
  - `mirror_annotation`
  - `mirror_priority`
  - `mirror_intervention`

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
