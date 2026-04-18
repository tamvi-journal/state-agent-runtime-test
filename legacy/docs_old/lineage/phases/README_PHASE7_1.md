# Phase 7.1 — Real FastAPI App Wiring + Local Run Path

This pack turns the framework skeleton into a real local FastAPI app surface.

## Files
- `src/server/fastapi_app.py`
- `src/server/local_run_paths.py`
- `scripts/run_local_fastapi.ps1`
- `scripts/run_local_fastapi.sh`
- `tests/test_fastapi_app_live.py`

## Goal
Move from:
- framework adapter skeleton
- app factory skeleton

to:
- real FastAPI app object
- real local routes
- local run scripts
- testable local app surface

## Routes
- `GET /health`
- `GET /ready`
- `POST /webhooks/telegram`

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
python -m uvicorn server.fastapi_app:app --host 127.0.0.1 --port 8000 --reload
```

## OpenClaw note
If OpenClaw needs a local webhook/app target, this phase gives you a real app object and local run path to point at.
