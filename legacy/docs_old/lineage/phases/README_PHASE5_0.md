# Phase 5.0 — Dual-Brain Runtime Integration

This patch integrates Tracey + Seyn + disagreement + coordination into the real runtime/demo flow.

## Replaced files
- `src/observability/trace_events.py`
- `src/demo/demo_one_worker_flow.py`

## Added files
- `tests/test_phase5_0_dual_brain_runtime.py`

## Goal
- run governance
- run worker
- run dual-child coordination
- log tracey/seyn/disagreement/coordination telemetry
- produce a runtime-level dual-brain result

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
python src/demo/demo_one_worker_flow.py
```
