# Local OpenClaw Cookbook

## Goal

Use the current local FastAPI app with OpenClaw or simple local probes without guessing payload shape.

## 1. Start the app

PowerShell:
```powershell
./scripts/run_app_local.ps1
```

## 2. Confirm the app is alive

- `GET http://127.0.0.1:8000/health`
- `GET http://127.0.0.1:8000/ready`

## 3. Use the OpenClaw adapter shape

Current easiest local path:
- convert a simple OpenClaw-style request
- send it to:
  - `POST /webhooks/telegram`

Relevant files:
- `src/shell/openclaw_local_adapter.py`
- `src/shell/openclaw_local_client_examples.py`

## 4. Good first probes

### Plain text
- `hello there`

### Builder probe
- `inspect current run`

### Runtime-heavy probe
- `Tracey, this is home, but verify whether MBB daily data is actually done.`

## 5. Useful side endpoints

- `GET /operator/latest`
- `GET /operator/session`
- `GET /debug/runtime-shape`
- `GET /debug/run-sample`

## 6. What to inspect

Look for:
- accepted webhook response
- non-empty outbound message
- runtime shape present
- routing present
- reconciliation present
- operator snapshot available

## 7. If something breaks

Check first:
- `SAMPLE_DATA_PATH`
- local venv
- `PYTHONPATH=src`
- whether sample CSV exists at `data/sample_market_data.csv`
