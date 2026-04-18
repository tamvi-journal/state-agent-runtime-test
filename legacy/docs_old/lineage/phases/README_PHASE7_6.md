# Phase 7.6 — Local Operator / Debug Endpoints

This pack adds local internal endpoints for operator and debug inspection.

## Files
- `src/server/operator_debug_contract.py`
- `src/server/operator_debug_provider.py`
- `src/server/fastapi_app.py`
- `tests/test_local_operator_debug_endpoints.py`

## Goal
Add local-only internal routes:
- `GET /operator/latest`
- `GET /operator/session`
- `GET /debug/runtime-shape`
- `GET /debug/run-sample`

These routes help local inspection without requiring raw log digging.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
python -m uvicorn server.fastapi_app:app --host 127.0.0.1 --port 8000 --reload
```
