# OpenClaw Local Examples

## Curl example

```bash
curl -X POST http://127.0.0.1:8000/webhooks/telegram \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## Python requests example

```python
import requests

payload = {
    "update_id": 10001,
    "message": {
        "message_id": 501,
        "text": "/builder inspect current run",
        "chat": {"id": 777},
        "from": {
            "id": "openclaw",
            "username": "openclaw",
            "first_name": "OpenClaw",
        },
    },
}

resp = requests.post("http://127.0.0.1:8000/webhooks/telegram", json=payload)
print(resp.status_code)
print(resp.json())
```

## Suggested local probes

- plain user text
- builder mode text
- Tracey/Seyn mixed runtime text
- operator/debug endpoints in parallel
