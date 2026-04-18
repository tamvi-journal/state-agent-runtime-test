# Thin Harness Tests

## Run

From repo root:

```powershell
$env:PYTHONPATH = "src"
pytest -q
```

## What this locks

- runtime harness wiring
- compact baton shape
- main-brain synthesis
- monitor summary compression
- gate decision behavior
- market_data_worker happy path
- market_data_worker missing file / missing ticker
- verification loop passed / failed / unknown
- runtime flow final synthesis on pass/fail path
