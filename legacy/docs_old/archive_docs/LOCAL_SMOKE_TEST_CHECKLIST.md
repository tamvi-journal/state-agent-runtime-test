# Local Smoke Test Checklist

## Goal

Validate that the local app is not just booting, but behaving along the intended boundary chain:

- app surface
- webhook boundary
- transport
- shell
- runtime provider
- coordination / reconciliation
- operator / debug endpoints

---

## Pre-flight

Before smoke testing:

1. activate the virtual environment
2. install dependencies
3. confirm tests pass
4. run the local FastAPI app

PowerShell:
```powershell
./scripts/bootstrap_dev_env.ps1
./scripts/test_local.ps1
./scripts/run_app_local.ps1
```

---

## Core checks

### 1. Health endpoint
Request:
- `GET /health`

Expected:
- HTTP 200
- body contains `status=healthy`

### 2. Ready endpoint
Request:
- `GET /ready`

Expected:
- HTTP 200
- body contains `status=ready`

### 3. Basic Telegram webhook payload
Request:
- `POST /webhooks/telegram`

Payload:
- plain user text

Expected:
- accepted response
- outbound message exists
- no crash at webhook/transport/shell boundaries

### 4. Builder-style webhook payload
Request:
- `POST /webhooks/telegram`

Payload:
- `/builder inspect current run`

Expected:
- accepted response
- outbound message exists
- builder path survives adapter chain cleanly

### 5. Runtime-heavy text probe
Request:
- `POST /webhooks/telegram`

Payload:
- text mentioning Tracey/home/verification/MBB

Expected:
- accepted response
- runtime provider returns non-trivial result
- coordination/reconciliation path is visibly alive

---

## Operator checks

### 6. Operator latest
Request:
- `GET /operator/latest`

Expected:
- operator snapshot exists
- dashboard snapshot exists
- rendered console exists

### 7. Operator session
Request:
- `GET /operator/session`

Expected:
- items count increases after operator/latest has been called
- latest flag is true once a snapshot exists

---

## Debug checks

### 8. Runtime shape
Request:
- `GET /debug/runtime-shape`

Expected:
- `has_final_response = true`
- `has_routing = true`
- `has_reconciliation = true`
- `has_context_view = true`

### 9. Sample runtime debug
Request:
- `GET /debug/run-sample`

Expected:
- runtime shape remains complete
- worker path may be active depending on text
- route should not crash

---

## Failure patterns to watch

### A. Server boots but webhook fails
Likely boundary mismatch in:
- webhook parser
- transport bridge
- runtime provider

### B. Accepted response but empty outbound
Likely shell/render issue.

### C. Operator/debug endpoints work but webhook path fails
Likely Telegram adapter / webhook payload shape mismatch.

### D. Runtime shape missing key sections
Likely runtime provider drift or app wiring drift.

### E. Tests pass but local run fails
Likely env/bootstrap issue:
- missing dependency
- wrong PYTHONPATH
- wrong local venv
- uvicorn not installed

---

## Success definition

The local run is “good enough” for this phase when:

- app starts locally
- health + ready pass
- webhook accepts plain text
- webhook accepts builder-style text
- operator endpoints return useful payload
- debug endpoints return runtime shape
- no boundary layer crashes during the path
