# Phase 5.5 — Coordination Refinement Pack

This pack refines coordination using governance posture, not just raw disagreement severity.

## Files
- `src/runtime/coordination_policy.py`
- `src/runtime/coordination_policy_engine.py`
- `src/runtime/dual_brain_router.py`
- `tests/test_coordination_refinement.py`

## Goal
Improve:
- hold thresholds
- lead/support routing
- disagreement surfacing
- coordination telemetry reasons
- governance-aware coordination behavior

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
