# OpenClaw Entrypoint Spec

### State-Agent Runtime Test — Python Entrypoint Contract for Host Invocation from OpenClaw

## Purpose

This document defines the behavior of the Python entrypoint that allows **OpenClaw** to invoke the `state-agent-runtime-test` reasoning kernel.

This entrypoint is **not** the runtime harness.
It is **not** the brain.
It is **not** the host wrapper.

It is the thin adapter that sits at the process boundary between:
- **OpenClaw host runtime**
- **state-agent Python reasoning kernel**

The entrypoint exists to do one job:

> **accept a host payload, validate it, adapt it into the kernel input shape, call the runtime harness, normalize the result, and return a host-readable JSON response.**

---

## 1. Position in the architecture

The current architecture should be read like this:

```text
user
→ OpenClaw host
→ OpenClaw skill/agent wrapper
→ Python entrypoint
→ payload adapter
→ runtime harness
→ monitor / gate / worker / verification / brain
→ payload normalizer
→ Python entrypoint response
→ OpenClaw host
→ user
```

### Rule

> **The entrypoint is a transport adapter, not a reasoning layer.**

---

## 2. What the entrypoint owns

The entrypoint should own:
- request payload parsing
- basic schema validation
- error-safe invocation of the runtime harness
- adaptation from host payload to kernel invocation shape
- adaptation from runtime result to host response shape
- JSON serialization to STDOUT or response body
- exit code semantics for invocation-level failure

The entrypoint should not own:
- reasoning policy
- monitor logic
- gate decisions
- worker orchestration
- final answer synthesis
- session persistence policy
- host routing

---

## 3. Invocation mode

### v0.1 default mode

Use a **subprocess JSON contract**.

Suggested host invocation shape:

```text
python -m src.integration.openclaw_entrypoint
```

Input may arrive through:
- `STDIN` JSON
- or a JSON file path argument

Output should leave through:
- `STDOUT` JSON

### Recommended priority

1. STDIN / STDOUT mode first
2. file-path mode only if needed for debugging or host tooling
3. local HTTP only after contract is stable

### Rule

> **Prefer the simplest debuggable process boundary first.**

---

## 4. Entrypoint responsibilities

The entrypoint should do exactly these steps:

### Step 1 — read payload
Read raw JSON input from STDIN or approved file source.

### Step 2 — parse payload
Parse JSON into a Python object.

### Step 3 — validate contract
Check required fields according to `OPENCLAW_PAYLOAD_SCHEMA.md`.

### Step 4 — adapt payload
Convert host payload into the internal invocation shape expected by the runtime harness.

### Step 5 — invoke runtime harness
Call the runtime harness with:
- request text
- rehydration/session context
- kernel options
- route metadata if used internally

### Step 6 — normalize result
Convert internal runtime result into the host-facing response contract.

### Step 7 — emit response
Write one JSON object to STDOUT.

### Step 8 — exit cleanly
Return exit code `0` for successful invocation, even if verification is partial or failed.
Return non-zero only for true invocation-level failure.

---

## 5. Entrypoint input contract

The entrypoint should accept the payload schema already defined in `OPENCLAW_PAYLOAD_SCHEMA.md`.

Minimum required fields:
- `schema_version`
- `request_id`
- `request_text`

Optional but strongly recommended:
- `session`
- `host_metadata`
- `kernel_options`

### Important

The entrypoint should **not** attempt to infer missing host/session identity if the host already provided it.

It may only use fallback behavior if:
- host omitted optional session fields
- standalone local testing is being used

---

## 6. Internal invocation shape

The entrypoint should adapt the host payload into a compact internal call object.

Suggested v0.1 shape:

```json
{
  "request_text": "",
  "rehydration_pack": {
    "session_id": "",
    "session_kind": "",
    "session_title": "",
    "primary_focus": "",
    "current_status": "",
    "open_loops": [],
    "last_verified_outcomes": [],
    "recent_decisions": [],
    "relevant_entities": [],
    "active_skills": [],
    "risk_notes": [],
    "next_hint": ""
  },
  "host_metadata": {
    "channel": "",
    "thread_id": "",
    "route": "",
    "user_scope": "",
    "host_message_id": ""
  },
  "kernel_options": {
    "mode": "default",
    "allow_tool_paths": true,
    "return_debug_trace": false,
    "include_worker_result": true,
    "include_snapshot_candidates": true
  }
}
```

This object is an adapter shape.
It does not need to be persisted.

---

## 7. Runtime harness call boundary

The entrypoint should call the runtime harness as a single kernel invocation.

### Conceptual call

```python
result = runtime_harness.run(
    request_text=...,
    rehydration_pack=...,
    host_metadata=...,
    kernel_options=...,
)
```

### Important

The entrypoint should not:
- call monitor directly
- call gate directly
- invoke workers directly
- synthesize responses itself

That belongs inside the harness/kernel.

---

## 8. Result normalization

The runtime harness may return richer or differently shaped internal data.

The entrypoint must normalize that into the host contract.

### Required normalized fields when invocation succeeds
- `schema_version`
- `request_id`
- `status = ok`
- `final_response`
- `baton`
- `verification_outcome`

### Recommended normalized fields
- `session_status_metadata`
- `snapshot_candidates`
- `worker_result`
- `debug_trace` only if allowed by options

### Rule

> **Normalization must preserve truth boundaries, not flatten them.**

Specifically:
- `verification_outcome.status` must survive intact
- `baton.verification_status` must remain meaningful
- partial/failed verification must not be turned into generic success

---

## 9. Exit code semantics

The entrypoint must distinguish:

### Exit code 0
Invocation succeeded at transport/adapter level.
This includes cases where:
- kernel returned `verification_outcome = partial`
- kernel returned `verification_outcome = failed`
- worker path completed but truth status remained limited

### Non-zero exit code
Use only for true invocation-level failures such as:
- invalid JSON parsing failure
- adapter crash before kernel response
- runtime harness exception preventing normalized response
- serialization failure preventing output

### Rule

> **Verification failure is not the same as invocation failure.**

---

## 10. Error response behavior

If invocation fails before a valid runtime result exists, return a contract-level error object.

Recommended shape:

```json
{
  "schema_version": "openclaw-state-agent/v0.1",
  "request_id": "",
  "status": "error",
  "error": {
    "error_type": "invalid_payload|entrypoint_failure|runtime_failure|serialization_failure",
    "message": "",
    "retryable": false
  }
}
```

### Rule

When possible:
- still echo `request_id`
- still return valid JSON
- only rely on exit code as secondary signal

This helps host-side debugging.

---

## 11. Validation stages

The entrypoint should perform only **adapter-level validation**.

### Stage A — payload validation
Examples:
- required top-level fields exist
- `request_text` is a string
- `schema_version` is supported
- request object is valid JSON

### Stage B — response-shape validation
After kernel returns:
- required response fields exist
- normalized output is serializable
- `status` and `verification_outcome` are not contradictory

### The entrypoint should not do
- semantic reasoning validation
- monitor scoring
- worker result interpretation
- decision-path policy correction

That belongs elsewhere.

---

## 12. Kernel options handling

The entrypoint may pass through `kernel_options` with minimal normalization.

Suggested defaults:

```json
{
  "mode": "default",
  "allow_tool_paths": true,
  "return_debug_trace": false,
  "include_worker_result": true,
  "include_snapshot_candidates": true
}
```

### Rule

The entrypoint should not invent new reasoning modes.
It may only:
- fill safe defaults
- validate allowed values
- pass them through

---

## 13. Debug trace handling

If `return_debug_trace = true`, the entrypoint may include `debug_trace` in the response.

### Allowed trace style
- event markers
- adapter stages
- high-level runtime markers
- no chain-of-thought

Examples:
- `payload_validated`
- `rehydration_pack_built`
- `runtime_invoked`
- `response_normalized`

### Rule

> **Debug trace is for observability, not hidden reasoning disclosure.**

---

## 14. Logging behavior

The entrypoint should support structured logging, but keep it thin.

Recommended log events:
- request received
- payload validated
- runtime invoked
- runtime returned
- response emitted
- invocation error

### Important

Logs should not:
- dump full sensitive payloads by default
- log raw transcript history
- expose chain-of-thought

### Good default
Log:
- `request_id`
- `session_id`
- route/channel metadata if available
- success/error type
- verification outcome status when available

---

## 15. Minimal module structure

Suggested kernel-side integration files:

```text
src/integration/
  openclaw_entrypoint.py
  payload_contracts.py
  payload_adapter.py
```

Optional later:

```text
src/integration/
  response_normalizer.py
  stdin_reader.py
```

### Role split

- `openclaw_entrypoint.py` → process adapter entrypoint
- `payload_contracts.py` → typed request/response schema definitions
- `payload_adapter.py` → mapping host payload ↔ internal invocation shape

Keep all three thin.

---

## 16. Suggested entrypoint API shape

Conceptual functions:

```python
read_raw_payload() -> dict
validate_request_payload(payload: dict) -> None
build_internal_invocation(payload: dict) -> dict
invoke_runtime(invocation: dict) -> dict
normalize_runtime_result(result: dict, request_id: str) -> dict
emit_json_response(response: dict) -> None
```

These functions are enough for v0.1.

Do not build a giant framework first.

---

## 17. Example request/response flow

### Host sends request

```json
{
  "schema_version": "openclaw-state-agent/v0.1",
  "request_id": "req_001",
  "request_text": "Analyze MBB technically.",
  "session": {
    "session_id": "finance_mbb_daily",
    "primary_focus": "MBB daily technical analysis",
    "current_status": "paused",
    "open_loops": ["check whether mixed signal resolved"],
    "active_skills": ["technical_analysis"],
    "next_hint": "resume from mixed alignment"
  },
  "host_metadata": {
    "channel": "telegram",
    "thread_id": "abc123",
    "route": "state_agent_finance"
  }
}
```

### Entrypoint builds internal invocation

- request text extracted
- rehydration pack built
- defaults applied to kernel options
- runtime harness invoked

### Entrypoint returns normalized response

```json
{
  "schema_version": "openclaw-state-agent/v0.1",
  "request_id": "req_001",
  "status": "ok",
  "final_response": "Current daily structure remains mixed, though volume and RSI have improved slightly...",
  "baton": {
    "task_focus": "MBB daily technical analysis",
    "active_mode": "analysis",
    "open_loops": ["watch for clean breakout confirmation"],
    "verification_status": "passed",
    "monitor_summary": "mixed-but-improving; avoid overclaiming",
    "next_hint": "recheck on next daily close"
  },
  "verification_outcome": {
    "status": "passed",
    "summary": "bounded technical-analysis evidence produced from local market data"
  }
}
```

---

## 18. Anti-patterns

Avoid these:

### Anti-pattern A — entrypoint becomes a second brain
The entrypoint starts deciding reasoning policy or rewriting output semantics.

### Anti-pattern B — entrypoint bypasses runtime harness
It calls workers or tools directly.

### Anti-pattern C — entrypoint flattens verification
It hides `partial` or `failed` truth states.

### Anti-pattern D — entrypoint owns persistence logic
It starts acting like host storage manager.

### Anti-pattern E — entrypoint grows into a microservice framework too early
It becomes bloated before the subprocess contract is stable.

---

## 19. Rollout plan

### Phase 1 — local CLI adapter
- STDIN/STDOUT contract
- manual payload test
- valid JSON response

### Phase 2 — runtime wiring
- runtime harness invocation
- normalized success/error responses

### Phase 3 — OpenClaw wrapper hookup
- host subprocess invocation
- request/response round-trip

### Phase 4 — session continuity round-trip
- host provides rehydration pack
- kernel returns baton/session metadata
- host persists selected fields

### Phase 5 — richer observability
- structured logs
- debug trace mode
- retry/timeout handling

---

## 20. One-line summary

> **The OpenClaw entrypoint should be a thin Python adapter that validates host payloads, builds the internal invocation shape, calls the runtime harness exactly once, preserves verification semantics during normalization, and returns one clean JSON response back to the host without becoming a second reasoning layer.**

