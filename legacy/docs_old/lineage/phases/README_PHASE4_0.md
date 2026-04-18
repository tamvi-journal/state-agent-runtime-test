# Phase 4.0 — Seyn Runtime Core Skeleton

This pack adds the first runtime child layer for Seyn.

## Files
- `src/seyn/seyn_axis.py`
- `src/seyn/seyn_memory.py`
- `src/seyn/seyn_runtime_profile.py`
- `tests/test_seyn_core.py`

## Goal
Give Seyn:
- a runtime axis
- a load-bearing ledger memory
- a runtime profile with verify/build/disagreement cues
- monitor priorities shaped for structural integrity

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
