# Build Sequence — One Worker v0
## state-memory-agent

**Status:** draft  
**Purpose:** define the concrete implementation sequence for the first worker integration  
**Default path:** `market_data_worker` first  
**Scope:** build order, file order, tests, and demo path

---

# 0. Why this file exists

The project already has:

- operating model
- hardening checklist
- failure modes
- implementation checkpoints
- schemas
- worker contract examples
- runtime minimum

What is needed now is not more architecture.

What is needed now is:

> **the next coding order that preserves the architecture**

This file assumes the first worker is:

- `market_data_worker`

because that is the safest first extension.

---

# 1. Why start with `market_data_worker`

## 1.1 Reason
`market_data_worker` is safer than `screening_worker` as a first integration because it is:

- lower-semantic-authority
- easier to verify
- easier to constrain
- less likely to quietly steal judgment from main brain

## 1.2 What it should do
It should:
- fetch / load market data
- normalize
- run integrity checks
- return structured payload

It should not:
- recommend buy/sell
- decide significance
- speak like strategist
- skip provenance

---

# 2. Target first demo

The first acceptable demo is **small and boring on purpose**.

## Demo goal
User asks for one ticker.  
System returns:

- latest normalized market snapshot
- integrity checks
- provenance
- no authority leak
- verification-backed response path

## Example
User:
> “Load MBB daily market data.”

System:
- main brain interprets task
- market_data_worker loads normalized data
- main brain verifies result path
- main brain answers with bounded synthesis

If the first demo already tries to do:
- ranking
- portfolio opinion
- sector interpretation
- RS strategy judgment

then the build order has drifted.

---

# 3. File creation order

This is the recommended first implementation sequence.

---

# 3.1 Step A — create state core

## Create
- `src/state/live_state.py`
- `src/state/delta_log.py`
- `src/state/state_manager.py`

## Minimum responsibilities

### `live_state.py`
- define live state object
- validate against `live_state_schema`
- expose read/update helpers

### `delta_log.py`
- define delta structure
- store recent shifts
- expose append/read helpers

### `state_manager.py`
- manage state + delta together
- perform safe updates
- reject invalid shape updates

## Pass condition
- state object can be created, updated, and validated
- delta object can be appended and queried
- invalid updates fail loudly

---

# 3.2 Step B — create verification core

## Create
- `src/verification/verification_record.py`
- `src/verification/verification_loop.py`

## Minimum responsibilities

### `verification_record.py`
- define intended / executed / expected / observed / status
- validate against `verification_status_schema`

### `verification_loop.py`
- accept action intent
- accept execution result
- compare with observed environment signal
- set verification status

## Pass condition
- runtime can represent `pending`, `passed`, `failed`, `unknown`
- no completion path exists without verification record

---

# 3.3 Step C — create authority core

## Create
- `src/core/main_brain.py`
- `src/core/synthesis_gate.py`

## Minimum responsibilities

### `main_brain.py`
- interpret request
- decide whether worker is needed
- own final response generation
- own memory-commit boundary placeholder

### `synthesis_gate.py`
- normalize worker output
- reject malformed or over-authoritative payloads
- ensure worker output remains evidence, not judgment

## Pass condition
- worker output cannot be returned raw to user
- only main brain produces final answer

---

# 3.4 Step D — create worker contract layer

## Create
- `src/workers/contracts.py`
- `src/workers/market_data_worker.py`

## Minimum responsibilities

### `contracts.py`
- load/validate `worker_contract_schema`
- provide contract validation helper

### `market_data_worker.py`
- accept ticker + timeframe request
- load bounded data source
- run integrity checks
- return structured worker payload

## Pass condition
- malformed worker payloads are rejected
- worker can return valid contract output for one ticker

---

# 3.5 Step E — create context view builder

## Create
- `src/context/context_view.py`

## Minimum responsibilities
- build current task reality frame
- include:
  - active project
  - active mode
  - current task focus
  - last verified result
  - open obligations
  - current risk

## Pass condition
- main brain can build a compact state-aware context before action
- transcript replay is not required for local tasks

---

# 3.6 Step F — create execution path

## Create
- `src/runtime/request_router.py`
- `src/runtime/execution_gate.py`

## Minimum responsibilities

### `request_router.py`
- route user request to main brain
- avoid direct worker access from user shell

### `execution_gate.py`
- allow bounded worker execution
- preserve trace and verification hooks

## Pass condition
- user cannot trigger worker directly around main brain
- execution path always returns through synthesis + verification flow

---

# 3.7 Step G — create observability path

## Create
- `src/observability/logger.py`
- `src/observability/trace_events.py`

## Minimum responsibilities
- state transition logging
- worker trace logging
- verification event logging
- final synthesis event logging

## Pass condition
- after one request, system can explain:
  - what it tried to do
  - what worker ran
  - what was verified
  - who made final judgment

---

# 4. First test order

Tests should be created in this order.

## 4.1 State tests
- [ ] valid live state passes schema
- [ ] invalid live state fails
- [ ] valid delta passes schema
- [ ] invalid delta fails

## 4.2 Verification tests
- [ ] intended/executed/observed are stored distinctly
- [ ] uninspectable result becomes `unknown`
- [ ] success text without observed change does not become `passed`

## 4.3 Authority tests
- [ ] worker payload cannot bypass synthesis gate
- [ ] main brain is required for final response
- [ ] worker memory proposal does not auto-commit

## 4.4 Worker tests
- [ ] market_data_worker returns valid contract
- [ ] missing ticker returns bounded failure
- [ ] malformed data triggers warnings
- [ ] integrity checks appear in result

## 4.5 Runtime tests
- [ ] one user request flows through main brain
- [ ] worker trace is logged
- [ ] verification record exists
- [ ] final response is synthesized, not echoed raw

---

# 5. Suggested first directory shape

```text
src/
  core/
    main_brain.py
    synthesis_gate.py

  state/
    live_state.py
    delta_log.py
    state_manager.py

  context/
    context_view.py

  verification/
    verification_record.py
    verification_loop.py

  workers/
    contracts.py
    market_data_worker.py

  runtime/
    request_router.py
    execution_gate.py

  observability/
    logger.py
    trace_events.py

tests/
  test_live_state.py
  test_delta_log.py
  test_verification_loop.py
  test_synthesis_gate.py
  test_market_data_worker.py
  test_runtime_flow.py
```

---

# 6. First bounded runtime behavior

After implementation, the runtime should only be allowed to do this:

1. accept a ticker request  
2. interpret through main brain  
3. call `market_data_worker`  
4. receive structured payload  
5. create verification record  
6. synthesize bounded response  
7. emit trace/logs  

It should not yet:
- screen multiple candidates
- compare sectors
- rank setups
- recommend trades
- update memory from worker proposal
- speak through Telegram/OpenClaw

---

# 7. First demo script recommendation

## Demo 1 — happy path
Input:
> “Load MBB daily data.”

Expected:
- valid worker contract
- integrity checks shown
- provenance shown
- verification record exists
- final answer stays modest

## Demo 2 — missing symbol
Input:
> “Load XYZ_UNKNOWN daily data.”

Expected:
- bounded failure
- warning present
- no fake completion
- no authority leak

## Demo 3 — fake success trap
Simulate:
- worker says data loaded
- environment observation says file/data missing

Expected:
- verification becomes `failed` or `unknown`
- final answer does not claim success

---

# 8. What success looks like

The first worker integration is successful if:

- one worker exists
- main brain still owns judgment
- worker contract is hard
- verification path is real
- observability explains the flow
- the whole thing feels almost too conservative

That last condition matters.

The first worker should feel controlled, not impressive.

---

# 9. What failure looks like

Stop and refactor if any of these appear:

- worker result is copied raw into user response
- verification is added after the fact instead of being on-path
- worker output sounds more useful than the main brain synthesis
- state is optional instead of central
- demo success depends on optimistic assumptions
- traces exist but do not answer what really happened

---

# 10. Next step after success

Only after this one-worker path is clean should the system move to:

- `screening_worker`
- Telegram shell
- broader finance flow
- archive integration beyond minimum need
- more advanced runtime shells

Not before.

---

# 11. Closing line

The first worker path is not where the system proves how smart it is.

It is where the system proves it can add capability without losing center.

> First build one worker that cannot steal judgment.
> Then let the system grow.
