# Phase 2.6 — Governance Integration Skeleton

This package adds a small integration layer that runs:

- Monitor
- Mirror Bridge
- Effort Allocator

in one turn-level governance pass.

## Files
- `src/runtime/governance_pass.py`
- `tests/test_governance_pass.py`

## Output
The governance pass returns:
- `monitor_output`
- `monitor_summary`
- `annotated_state`
- `effort_input`
- `effort_decision`

## Goal
Move from isolated governance modules
to a compact turn-level governance package that runtime/main_brain can consume.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
