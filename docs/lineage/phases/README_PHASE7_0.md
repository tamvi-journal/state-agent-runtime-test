# Phase 7.0 — Process Runner / Deployment Skeleton

This pack adds the first deployment-facing layer for the app.

## Files
- `src/deploy/runtime_config.py`
- `src/deploy/logging_bootstrap.py`
- `src/deploy/process_runner.py`
- `src/deploy/deployment_manifest.py`
- `tests/test_process_runner.py`

## Goal
Move from:
- framework/app skeleton

to:
- config loading
- logging bootstrap
- run-plan generation
- deployment manifest

Still excluded:
- no actual uvicorn launch
- no Docker entrypoint
- no supervisor/systemd config
- no cloud deployment descriptors

This is the first deployment/process boundary before live operations.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
