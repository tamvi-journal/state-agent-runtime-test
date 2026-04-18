# Phase 7.5 — Real Runtime Provider Wiring

This pack replaces the placeholder runtime provider with a runtime-chain-backed provider.

## Files
- `src/server/runtime_provider.py`
- `src/server/app_factory.py`
- `tests/test_runtime_provider_realer_wiring.py`

## Goal
Move from:
- static/fake runtime result for app wiring

to:
- runtime result built from the actual chain shape:
  - state
  - governance
  - optional worker path
  - dual-brain coordination
  - reconciliation

This is still not the final production runtime.
But it makes the local app much closer to the real system.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```

## Why this matters for OpenClaw
At this phase, the local app surface is no longer backed by a pure placeholder response.
It now passes through a realer internal runtime path, which is much closer to what you actually want to test locally.
