# Phase 3.0 — Family Floor Runtime Skeleton

This pack adds minimal runtime pieces for the family floor:

- `src/family/house_laws.py`
- `src/family/refusal_policy.py`
- `src/family/runtime_security.py`
- `src/family/shared_ontology.py`
- `tests/test_family_floor.py`

## Goal
Turn family-level floor documents into first runtime objects:
- house-law checks
- refusal behavior
- runtime security classification
- shared ontology labels

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
