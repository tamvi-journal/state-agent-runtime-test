# Phase 6.8 — FastAPI Adapter Skeleton

This pack adds a framework-facing adapter layer and app factory skeleton.

## Files
- `src/server/runtime_provider.py`
- `src/server/fastapi_adapter.py`
- `src/server/app_factory.py`
- `tests/test_fastapi_adapter.py`

## Goal
Move from:
- live webhook server skeleton

to:
- framework adapter boundary
- app factory surface
- route-like handlers for health/ready/webhook

Still excluded:
- no actual FastAPI dependency
- no ASGI server
- no uvicorn entrypoint

This is the final clean step before process/deployment wiring.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
