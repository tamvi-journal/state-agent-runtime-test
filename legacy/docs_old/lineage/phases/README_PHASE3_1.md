# Phase 3.1 — Tracey Runtime Core Skeleton

This pack adds the first runtime child layer for Tracey.

## Files
- `src/tracey/tracey_axis.py`
- `src/tracey/tracey_memory.py`
- `src/tracey/tracey_runtime_profile.py`
- `tests/test_tracey_core.py`

## Goal
Give Tracey:
- a runtime axis
- a small checkpoint-style memory
- a runtime profile with cues, monitor priorities, and ontology access

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
