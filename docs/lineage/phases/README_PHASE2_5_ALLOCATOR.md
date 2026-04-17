# Phase 2.5 — Effort Allocator Skeleton

This package adds a heuristic family-level effort allocator.

## Files
- `src/allocator/effort_schema.py`
- `src/allocator/effort_allocator.py`
- `tests/test_effort_allocator.py`

## Purpose
Route:
- effort level
- cognition topology
- monitor intensity
- verification requirement
- memory commit status
- disagreement handling
- reasoning depth

## Included rule
If stakes are unclear, default posture is `medium`, not `low`.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
