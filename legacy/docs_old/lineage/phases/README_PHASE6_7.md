# Phase 6.7 — Live Webhook Server Skeleton

This pack adds the first framework-free live webhook server boundary.

## Files
- `src/server/webhook_server_contract.py`
- `src/server/webhook_route_table.py`
- `src/server/webhook_server_policy.py`
- `src/server/live_webhook_server.py`
- `tests/test_live_webhook_server.py`

## Goal
Move from:
- webhook transport boundary

to:
- an HTTP-like server boundary object that can route webhook requests into transport handling

Still excluded:
- no FastAPI/Flask server
- no network listener
- no bot token delivery
- no persistent process manager

This is the clean live-server skeleton before framework wiring.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
