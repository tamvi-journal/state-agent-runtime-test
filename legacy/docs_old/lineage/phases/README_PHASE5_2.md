# Phase 5.2 — Unresolved Disagreement Requirement Test Pack

This pack adds a guard object and tests for the core plurality requirement:

> the system must be able to keep one disagreement open
> without fake consensus or fake completion overlay.

## Files
- `src/family/unresolved_disagreement_guard.py`
- `tests/test_unresolved_disagreement_requirement.py`

## Goal
Check that:
- shared disagreement stays open
- both local perspectives remain preserved
- no epistemic resolution is falsely claimed
- final response does not overlay fake closure on open disagreement

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
