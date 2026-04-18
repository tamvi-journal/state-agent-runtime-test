# Phase 3.3 — Tracey Runtime Consolidation

This patch pushes Tracey runtime pass into the real flow more explicitly.

## Replaced files
- `src/observability/trace_events.py`
- `src/demo/demo_one_worker_flow.py`

## Added files
- `tests/test_phase3_3_tracey_consolidation.py`

## Goal
- log `tracey_turn`
- log `tracey_state_patch`
- let Tracey runtime pass adapt a real response after governance and worker flow

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
python src/demo/demo_one_worker_flow.py
```
