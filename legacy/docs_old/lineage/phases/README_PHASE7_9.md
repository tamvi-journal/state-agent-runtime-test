# Phase 7.9 — Local Run Stabilization + Sample Data / Config Cleanup

This pack stabilizes the local loop for app + OpenClaw-style testing.

## Files
- `data/sample_market_data.csv`
- `config/local.runtime.env.example`
- `src/server/runtime_provider.py`
- `scripts/run_local_validation.ps1`
- `scripts/run_local_validation.sh`
- `docs/LOCAL_OPENCLAW_COOKBOOK.md`
- `docs/LOCAL_STABILIZATION_NOTES.md`
- `tests/test_local_stabilization_artifacts.py`

## Goal
Move from:
- local app works if the builder knows the right assumptions

to:
- local loop has a clearer sample data path
- local env shape is more explicit
- local validation has a short sanity runner
- OpenClaw local testing has a cookbook
