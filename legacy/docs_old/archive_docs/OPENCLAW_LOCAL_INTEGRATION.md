# OpenClaw Local Integration

## Goal

Use the local FastAPI app as a target for OpenClaw/local manual testing.

Current local route:
- `POST /webhooks/telegram`

The current app already accepts Telegram-shaped webhook payloads.
This phase adds a thin adapter so OpenClaw local testing can stay simple.

---

## Simplest local idea

Treat OpenClaw local messages as:
- plain text input
- optional mode (`user` / `builder`)
- optional trace intent

Then convert them into the currently supported Telegram webhook payload shape.

---

## Adapter object

See:

- `src/shell/openclaw_local_adapter.py`

It converts a small request like:

```python
{
  "text": "inspect current run",
  "mode": "builder",
  "wants_builder_view": True
}
```

into a webhook JSON body the app already understands.

---

## Example request bodies

### User-like
```json
{
  "update_id": 10001,
  "message": {
    "message_id": 501,
    "text": "hello there",
    "chat": { "id": 777 },
    "from": {
      "id": "openclaw",
      "username": "openclaw",
      "first_name": "OpenClaw"
    }
  }
}
```

### Builder-like
```json
{
  "update_id": 10001,
  "message": {
    "message_id": 501,
    "text": "/builder inspect current run",
    "chat": { "id": 777 },
    "from": {
      "id": "openclaw",
      "username": "openclaw",
      "first_name": "OpenClaw"
    }
  }
}
```

---

## Local run flow

### 1. Start the app
PowerShell:
```powershell
./scripts/run_app_local.ps1
```

### 2. Send a local POST
URL:
- `http://127.0.0.1:8000/webhooks/telegram`

### 3. Use a payload built by the adapter
That is enough for a first OpenClaw local integration loop.

---

## Practical note

This is not forcing OpenClaw to become “Telegram”.
It is only using the current supported webhook shape as the first local compatibility surface.

Later, if needed, a dedicated OpenClaw route can be added cleanly.
