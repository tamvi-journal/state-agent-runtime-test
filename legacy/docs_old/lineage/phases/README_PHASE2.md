# Phase 2 Skeleton — screening_worker

This package adds:
- `src/workers/screening_worker.py`
- `tests/test_screening_worker.py`
- `tests/test_main_brain_screening_phase2.py`

## Notes

This is intentionally a skeleton:
- screening stays mechanical
- no final recommendation
- no portfolio judgment
- same worker contract as market_data_worker

## Suggested next step after copy

You will likely want to extend `src/core/main_brain.py`
to render screening payloads more elegantly in both:
- builder mode
- user mode

## Run

```powershell
$env:PYTHONPATH = "src"
pytest -q
```
