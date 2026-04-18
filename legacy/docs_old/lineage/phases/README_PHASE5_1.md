# Phase 5.1 — Observability / Dashboard Pass

This pack adds a compact dashboard layer for the runtime chain.

## Files
- `src/observability/dashboard_summary.py`
- `src/observability/timeline_view.py`
- `src/observability/dashboard_snapshot.py`
- `tests/test_dashboard_snapshot.py`

## Goal
Provide readable views over:
- worker flow
- governance summary
- child signals
- disagreement
- reconciliation
- routing
- integrity flags
- event timeline

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
