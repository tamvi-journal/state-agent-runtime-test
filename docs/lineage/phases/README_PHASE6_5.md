# Phase 6.5 — Shell Transport Abstraction

This pack adds a transport layer above channel adapters and below future webhook/server transports.

## Files
- `src/transport/transport_contract.py`
- `src/transport/transport_policy.py`
- `src/transport/telegram_transport_mapper.py`
- `src/transport/transport_bridge.py`
- `tests/test_transport_abstraction.py`

## Goal
Separate:
- transport boundary
- channel adapter boundary
- shell/runtime boundary

This is the clean step before:
- Telegram webhook transport
- HTTP transport server
- CLI transport
- operator transport paths

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
