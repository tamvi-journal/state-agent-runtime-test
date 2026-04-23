# OpenClaw Integration Spec

### State-Agent Runtime Test — Host Integration Contract for Running the Python Reasoning Kernel on OpenClaw

## Purpose

This document defines how `state-agent-runtime-test` should integrate with **OpenClaw as the host runtime**.

The intended architecture is:

> **OpenClaw hosts. State-agent reasons.**

OpenClaw should handle:
- channel and user entrypoints
- thread/session routing
- host persistence
- sandbox and execution policy at the platform level
- skill registry and host-side orchestration
- optional multi-agent routing if needed later

State-agent should handle:
- the inner reasoning loop
- monitor / gate / verification discipline
- worker/tool orchestration inside the kernel
- baton emission
- session-status metadata updates
- structured reasoning outputs back to the host

This spec is therefore about **interop**, not replacement.

---

## 1. Core architecture thesis

State-agent is **not** trying to replace OpenClaw.

It is an opinionated **reasoning kernel** that plugs into OpenClaw.

The clean boundary is:

- **OpenClaw = runtime host**
- **state-agent = inner reasoning kernel**

That means the integration should avoid two bad designs:

### Bad design A — duplicate platform
Trying to rebuild OpenClaw sessioning, routing, skill registry, and sandbox inside state-agent.

### Bad design B — shallow wrapper
Calling state-agent from OpenClaw in a way that strips out session context, verification semantics, or baton continuity.

The correct design is:

> **thin host ↔ kernel interop layer with a strong contract.**

---

## 2. Integration mode

Recommended first integration mode:

> **OpenClaw invokes state-agent as an external skill/agent process.**

That means:
- no in-process import across Node/TS and Python
- no shared runtime memory assumptions
- communication happens across a process boundary or HTTP boundary

### Preferred order

#### Mode 1 — subprocess / CLI contract
Best for early development.

#### Mode 2 — local HTTP service
Best when iteration needs a stable service boundary.

#### Mode 3 — richer host orchestration
Only later, if OpenClaw-side routing grows more complex.

### Rule

Start with **process boundary first**.
Do not overbuild service infrastructure before the contract is stable.

---

## 3. Ownership boundary

### OpenClaw owns

- channel / user / thread identity
- host `session_id`
- routing and invocation policy
- host persistence
- skill selection policy
- sandbox / process permissions
- host-level timeout / retry posture
- delivery of final answer back to user

### State-agent owns

- reading the input contract
- reconstructing working posture from the rehydration pack
- monitor / gate / verification / brain loop
- worker execution inside the kernel boundary
- baton generation
- continuity metadata generation
- structured result payload for the host

### Rule

> **OpenClaw owns the outer loop. State-agent owns the inner loop.**

---

## 4. Primary interaction model

Recommended request path:

```text
user
→ OpenClaw channel/session/router
→ OpenClaw skill or external-agent invocation
→ state-agent input contract
→ state-agent runtime harness
→ monitor / gate / worker / verification / brain
→ structured result payload
→ OpenClaw host handling
→ user-facing output
```

This preserves the core value of each layer.

---

## 5. Invocation styles

## Style A — skill wrapper invocation

OpenClaw treats state-agent as a callable skill-like unit.

Use when:
- a specific route intentionally wants the state-agent reasoning kernel
- the host wants to pass a compact input payload and receive structured output
- the integration should look like one powerful skill within host orchestration

### Good fit
- builder tasks
- finance-analysis tasks
- bounded workflow analysis
- higher-discipline reasoning tasks

---

## Style B — external agent invocation

OpenClaw treats state-agent as an external agent runtime endpoint.

Use when:
- host routing needs to decide between multiple agents later
- state-agent needs to return richer metadata than a typical simple skill
- the kernel becomes a reusable reasoning backend across flows

### Rule

For v0.1, either style is acceptable.
The key is to keep the I/O contract stable.

---

## 6. Recommended v0.1 interface

Use a single structured JSON request/response contract.

### Input to state-agent

```json
{
  "request_text": "",
  "session": {
    "session_id": "",
    "session_kind": "analysis|builder|creative|workflow|general",
    "session_title": "",
    "primary_focus": "",
    "current_status": "active|paused|completed|blocked|unknown",
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
    "return_debug_trace": false
  }
}
```

### Output from state-agent

```json
{
  "final_response": "",
  "baton": {
    "task_focus": "",
    "active_mode": "",
    "open_loops": [],
    "verification_status": "",
    "monitor_summary": "",
    "next_hint": ""
  },
  "session_status_metadata": {
    "current_status": "active|paused|completed|blocked|unknown",
    "primary_focus": "",
    "open_loops": [],
    "last_verified_outcomes": [],
    "recent_decisions": [],
    "relevant_entities": [],
    "active_skills": [],
    "risk_notes": [],
    "next_hint": ""
  },
  "snapshot_candidates": [],
  "verification_outcome": {
    "status": "passed|partial|unknown|failed",
    "summary": ""
  },
  "worker_result": {
    "worker_name": "",
    "result": {}
  }
}
```

This should be the contract OpenClaw consumes.

---

## 7. Process boundary recommendation

### v0.1 recommendation

Use a **subprocess JSON contract**.

OpenClaw launches a Python entrypoint such as:

```text
python -m src.integration.openclaw_entrypoint
```

and passes the request payload through:
- STDIN
- or a temp JSON file path

State-agent returns JSON through:
- STDOUT
- or a result file path

### Why this is the best first step

- keeps Node/TS and Python cleanly separated
- easy to debug
- easy to inspect raw payloads
- no HTTP service management yet
- avoids premature daemonization

### Rule

Prefer **debuggable process IPC** over clever architecture in v0.1.

---

## 8. Entry point behavior

Suggested kernel entrypoint responsibilities:

1. parse incoming payload
2. validate required fields
3. build rehydration pack for runtime harness
4. invoke runtime harness
5. normalize runtime result into host contract
6. print JSON result
7. return non-zero exit code only for true invocation failure

The entrypoint should **not** contain reasoning logic.
It is only the interop adapter.

---

## 9. Host-side skill wrapper

If OpenClaw uses a skill-style wrapper, that wrapper should do only:

1. collect current message text
2. collect host session metadata
3. build compact session payload
4. invoke state-agent process
5. parse JSON response
6. persist or merge returned continuity metadata if desired
7. render `final_response` back to host flow

### It should not
- re-implement monitor/gate/verification logic
- reinterpret worker payload into a second brain
- flatten verification semantics into generic success language

### Rule

> **Wrapper is transport and persistence glue, not a competing reasoning layer.**

---

## 10. Session handoff model

OpenClaw should provide:
- `session_id`
- thread/session context
- compact prior continuity state if available

State-agent should return:
- baton
- session-status metadata
- snapshot candidates
- verification outcome

### Important

OpenClaw may choose to persist:
- all of it
- some of it
- or only selected fields

State-agent should not assume that every returned field is durably saved.

---

## 11. Skills interaction

When running under OpenClaw:

- OpenClaw may decide which skill or route invokes state-agent
- OpenClaw may pass `active_skills` or compact skill summaries into the request payload
- state-agent may consume those skill hints as reasoning context
- state-agent should not assume ownership of host-side skill registry or skill activation lifecycle

### Practical pattern

OpenClaw skill registry decides **what is available**.
State-agent decides **how to reason given the provided skill context**.

---

## 12. Gate interaction under host mode

State-agent’s internal gate still matters.

Even under OpenClaw, the kernel should keep its own reasoning boundary for:
- allow
- sandbox_only
- needs_approval
- deny

### Why

OpenClaw host policy and kernel gate are not duplicates.
They protect different layers:

- **host policy** = platform boundary
- **kernel gate** = reasoning-to-action boundary inside the kernel

### Rule

> **Host policy does not remove the need for kernel gate discipline.**

---

## 13. Verification interaction under host mode

State-agent should still return verification semantics explicitly.

OpenClaw should not collapse:
- tool executed
- worker returned
- verification passed

into one generic host success state.

### Minimum host preservation

Host should preserve at least:
- `verification_outcome.status`
- `verification_outcome.summary`
- `baton.verification_status`

### Rule

> **OpenClaw may host the kernel, but it should not flatten kernel truth boundaries.**

---

## 14. Failure semantics

The interop layer should distinguish these cases clearly.

### A. Invocation failure
Examples:
- Python process failed to start
- invalid JSON
- crash before runtime result

Host behavior:
- treat as infrastructure/invocation error

### B. Kernel completed but verification failed or partial
Examples:
- market data path missing
- blocked dependency
- partial evidence only

Host behavior:
- treat as valid kernel response with non-success verification semantics

### C. Host persistence failure after valid kernel result
Examples:
- session write failed
- snapshot merge failed

Host behavior:
- do not erase the kernel result
- surface host persistence issue separately if needed

This separation is important.

---

## 15. Minimal file plan for kernel side

Suggested new kernel-side files:

```text
src/integration/
  openclaw_entrypoint.py
  payload_contracts.py
  payload_adapter.py
```

Optional if needed later:

```text
src/integration/
  response_normalizer.py
```

Keep these files thin.
Do not let them become a second runtime harness.

---

## 16. Minimal file plan for host-side concept

This spec does not define exact OpenClaw code structure, but conceptually the host needs:

- a skill wrapper or agent wrapper
- a session payload builder
- a subprocess invoker or local HTTP client
- a response parser
- a persistence merge policy

Again, thin glue only.

---

## 17. Recommended rollout phases

### Phase 1 — static contract
- define input/output JSON schema
- add Python entrypoint
- test with local files and manual invocation

### Phase 2 — local OpenClaw wrapper
- host invokes the Python kernel through subprocess
- session payload is passed in minimally
- final response is returned to host

### Phase 3 — continuity merge
- host begins saving `session_status_metadata`
- host may restore compact session payload on next invocation

### Phase 4 — skill-aware invocation
- host passes active skill ids or summaries
- kernel consumes them as context

### Phase 5 — richer policy and observability
- better timeout handling
- retry posture
- structured logs
- host-side metrics

Do not jump to phase 5 first.

---

## 18. Practical example

### User asks via OpenClaw channel

> “Analyze MBB technically and continue from yesterday’s unfinished chart read.”

### OpenClaw provides input

```json
{
  "request_text": "Analyze MBB technically and continue from yesterday’s unfinished chart read.",
  "session": {
    "session_id": "finance_mbb_daily",
    "session_kind": "analysis",
    "primary_focus": "MBB daily technical analysis",
    "current_status": "paused",
    "open_loops": [
      "confirm invalidation condition",
      "check whether mixed signal resolved"
    ],
    "last_verified_outcomes": [
      "market data loaded yesterday",
      "prior read classified as mixed"
    ],
    "active_skills": ["technical_analysis"],
    "next_hint": "resume from mixed alignment and re-check volume"
  },
  "host_metadata": {
    "channel": "telegram",
    "thread_id": "abc123",
    "route": "state_agent_finance",
    "user_scope": "private"
  }
}
```

### State-agent returns

```json
{
  "final_response": "Current daily structure is still mixed, but volume has improved and RSI is no longer as weak. The read is stronger than yesterday, though not cleanly confirmed yet...",
  "baton": {
    "task_focus": "MBB daily technical analysis",
    "active_mode": "analysis",
    "open_loops": ["watch for clean breakout confirmation"],
    "verification_status": "passed",
    "monitor_summary": "mixed-but-improving; avoid overclaiming",
    "next_hint": "recheck on next daily close"
  },
  "session_status_metadata": {
    "current_status": "active",
    "primary_focus": "MBB daily technical analysis",
    "open_loops": ["watch for clean breakout confirmation"],
    "last_verified_outcomes": ["local market data loaded successfully", "daily read updated"],
    "recent_decisions": ["kept classification below full bullish confirmation"],
    "relevant_entities": ["MBB", "daily timeframe"],
    "active_skills": ["technical_analysis"],
    "risk_notes": ["confirmation still incomplete"],
    "next_hint": "recheck on next daily close"
  },
  "verification_outcome": {
    "status": "passed",
    "summary": "bounded technical-analysis evidence produced from local market data"
  }
}
```

OpenClaw then decides what to persist and how to render or route the result.

---

## 19. Anti-patterns

Avoid these:

- importing Python kernel directly into host runtime process
- letting the host wrapper become a second reasoning layer
- flattening verification into generic success
- forcing state-agent to own OpenClaw session storage
- replaying full host transcript into every kernel call
- overbuilding HTTP/microservice infrastructure before the subprocess contract is stable

---

## 20. One-line summary

> **OpenClaw should host state-agent through a thin, structured interop layer: the host provides session and routing context, the Python kernel performs the disciplined reasoning loop, and the host consumes final response plus continuity metadata without flattening monitor/gate/verification semantics.**

