# Phase 2.7 — Consolidation Patch

This patch pushes governance modules closer to the real runtime flow.

## Replaced files
- `src/observability/trace_events.py`
- `src/core/main_brain.py`
- `src/demo/demo_one_worker_flow.py`

## Added files
- `tests/test_phase2_7_consolidation.py`

## What changes
- governance telemetry logs added
- demo flow now runs governance pass pre/post action
- main_brain can read `monitor_summary`
- user output can reflect governance posture in a bounded way

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
python src/demo/demo_one_worker_flow.py
```
