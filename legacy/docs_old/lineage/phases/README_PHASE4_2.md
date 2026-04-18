# Phase 4.2 — Disagreement Register Skeleton

This pack adds the shared disagreement event layer for the family scaffold.

## Files
- `src/family/disagreement_event.py`
- `src/family/disagreement_register.py`
- `tests/test_disagreement_register.py`

## Goal
Create:
- shared disagreement events
- local perspective notes
- open/resolve behavior without erasing history
- action lead tracking without fake truth resolution

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
