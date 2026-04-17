# Local Stabilization Notes

## What this phase stabilizes

### Sample data
The runtime provider now resolves sample data path in this order:
1. explicit constructor value
2. `SAMPLE_DATA_PATH` env
3. fallback to `data/sample_market_data.csv`

### Config clarity
This phase adds:
- `config/local.runtime.env.example`
- `SAMPLE_DATA_PATH` example
- local validation scripts

### Validation path
Use:
- `scripts/run_local_validation.ps1`
- `scripts/run_local_validation.sh`

These are not full smoke tests for every endpoint.
They are quick sanity checks for:
- dependency presence
- runtime provider path
- test suite

## Why this matters

Without this cleanup, local app behavior may look flaky
only because sample data/config/bootstrap is inconsistent across runs.
