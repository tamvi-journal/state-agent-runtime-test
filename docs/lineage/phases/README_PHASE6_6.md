# Phase 6.6 — Telegram Webhook Transport Skeleton

This pack adds the webhook boundary object for Telegram transport.

## Files
- `src/transport/telegram_webhook_contract.py`
- `src/transport/telegram_webhook_parser.py`
- `src/transport/telegram_webhook_bridge.py`
- `src/transport/telegram_webhook_response.py`
- `tests/test_telegram_webhook_transport.py`

## Goal
Move from:
- Telegram adapter
- transport abstraction

to:
- webhook-shaped boundary parsing and routing

Still excluded:
- no actual HTTP server
- no bot token/network call
- no framework-specific webhook implementation

This is the clean webhook boundary before live transport.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
