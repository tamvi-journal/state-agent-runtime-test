# Local Troubleshooting

## 1. `No module named uvicorn`
Install dev dependencies:
```powershell
./scripts/bootstrap_dev_env.ps1
```

## 2. `No module named fastapi`
Same fix:
```powershell
./scripts/bootstrap_dev_env.ps1
```

## 3. Tests pass but app import fails
Check:
- venv is activated
- `PYTHONPATH=src`
- app command is using the project venv

PowerShell:
```powershell
$env:PYTHONPATH = "src"
python -m uvicorn server.fastapi_app:app --host 127.0.0.1 --port 8000 --reload
```

## 4. Webhook route returns rejected
Check:
- request method is POST
- JSON body is not empty
- payload contains message text

## 5. Webhook route accepts but response is weird
Check:
- input text shape
- builder prefix
- whether runtime provider is using sample data path that exists

## 6. Operator/debug endpoints crash
Check:
- runtime provider still returns:
  - final_response
  - routing
  - reconciliation
  - child_result
  - governance_output
  - context_view

## 7. OpenClaw local payload does not work
Use the adapter/examples from:
- `src/shell/openclaw_local_adapter.py`
- `docs/OPENCLAW_LOCAL_EXAMPLES.md`

## 8. App starts but port is busy
Change local port:
```powershell
python -m uvicorn server.fastapi_app:app --host 127.0.0.1 --port 8010 --reload
```
