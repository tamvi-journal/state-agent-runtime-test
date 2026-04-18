# Phase 6.4 — Telegram Adapter Skeleton

This pack adds the first Telegram-shaped adapter layer.

## Files
- `src/shell/telegram_contract.py`
- `src/shell/telegram_adapter.py`
- `src/shell/telegram_runtime_adapter.py`
- `tests/test_telegram_adapter.py`

## Goal
Move from:
- generic shell/runtime bridge

to:
- Telegram-shaped inbound/outbound payload handling

Still excluded:
- no webhook server
- no Telegram API calls
- no bot token logic

This is the clean adapter layer before transport.

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
