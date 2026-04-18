# Phase 4.3 — Disagreement Wiring

This pack wires Tracey and Seyn runtime outputs into a shared disagreement event layer.

## Files
- `src/family/disagreement_wiring.py`
- `src/runtime/dual_child_runtime_pass.py`
- `tests/test_disagreement_wiring.py`

## Goal
- run both child passes on one turn
- detect material divergence
- write one shared disagreement event
- write one local note per child
- preserve plurality without forced consensus

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
