# Phase 7.7 — OpenClaw Local Integration Notes + Adapter Cleanup

This pack adds a thin local compatibility layer for OpenClaw-style testing.

## Files
- `src/shell/openclaw_local_adapter.py`
- `src/shell/openclaw_local_client_examples.py`
- `docs/OPENCLAW_LOCAL_INTEGRATION.md`
- `docs/OPENCLAW_LOCAL_EXAMPLES.md`
- `tests/test_openclaw_local_adapter.py`

## Goal
Move from:
- generic local FastAPI app
- Telegram webhook-shaped local entry

to:
- a cleaner local testing path for OpenClaw/manual local calls

This phase does not change the core runtime.
It only makes the local integration path easier to use.
