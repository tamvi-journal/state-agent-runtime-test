# Phase 5.6 — Persistence / Archive Discipline

This pack adds initial persistence rules for plurality-related runtime objects.

## Files
- `src/state/persistence_policy.py`
- `src/state/archive_router.py`
- `src/state/plurality_persistence_snapshot.py`
- `tests/test_persistence_archive_discipline.py`

## Goal
Define:
- what persists
- what archives
- what remains ephemeral
- what may stay in live state
- what should decay quickly

Especially for:
- disagreement events
- local perspective notes
- reconciliation results
- child memory
- governance summaries

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
