# QUICKSTART

## Goal

Get the repo running locally in the shortest clean path.

## Step 1 — activate environment

PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

bash:
```bash
source .venv/bin/activate
```

## Step 2 — install dependencies

PowerShell:
```powershell
./scripts/bootstrap_dev_env.ps1
```

bash:
```bash
bash ./scripts/bootstrap_dev_env.sh
```

## Step 3 — run tests

PowerShell:
```powershell
./scripts/test_local.ps1
```

bash:
```bash
bash ./scripts/test_local.sh
```

## Step 4 — run app

PowerShell:
```powershell
./scripts/run_app_local.ps1
```

bash:
```bash
bash ./scripts/run_app_local.sh
```

## Step 5 — verify endpoints

- `GET http://127.0.0.1:8000/health`
- `GET http://127.0.0.1:8000/ready`

## Step 6 — test Telegram webhook path locally

POST to:
- `http://127.0.0.1:8000/webhooks/telegram`

with JSON body like:

```json
{
  "update_id": 10001,
  "message": {
    "message_id": 501,
    "text": "hello there",
    "chat": { "id": 777 },
    "from": {
      "id": 42,
      "username": "ty_user",
      "first_name": "Ty"
    }
  }
}
```

## Result

At this phase, the app should:
- accept the request
- parse Telegram-shaped payload
- route it through shell/transport/runtime boundary objects
- return a normalized accepted response
