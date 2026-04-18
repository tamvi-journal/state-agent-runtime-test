# Phase 4.1 — Seyn Integration Pass

This pack integrates Seyn core into runtime flow as a light child-layer.

## Files
- `src/seyn/seyn_adapter.py`
- `src/runtime/seyn_runtime_pass.py`
- `tests/test_seyn_integration.py`

## Goal
Let Seyn:
- inspect a turn
- detect verify/build/disagreement hint
- reactivate ledger items
- patch runtime state lightly
- adapt response in a bounded way

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
