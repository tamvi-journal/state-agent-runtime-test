# Phase 4.4 — Simple Dual-Brain Coordination Pass

This pack adds a minimal coordination layer above Tracey/Seyn dual-child observation.

## Files
- `src/runtime/dual_brain_router.py`
- `src/runtime/dual_brain_coordination_pass.py`
- `tests/test_dual_brain_coordination.py`

## Goal
- choose lead brain for action
- choose support brain
- optionally hold for more input
- optionally surface disagreement
- keep rule: action lead != truth resolution

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
