# Runtime Flow Tests Pack

Copy these files into your repo:

- tests/conftest.py
- tests/test_market_data_worker.py
- tests/test_verification_loop.py
- tests/test_execution_gate.py
- tests/test_runtime_flow.py

## Run

From repo root:

```powershell
$env:PYTHONPATH = "src"
pytest -q
```

If `pytest` is not installed:

```powershell
pip install pytest
```

## What this locks

- market_data_worker happy path
- market_data_worker missing file / missing ticker
- verification loop passed / failed / unknown
- execution gate emitted trace + verification events
- runtime flow final synthesis on pass/fail path
