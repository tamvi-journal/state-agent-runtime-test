> [!WARNING]
> **Historical merged operating model. Superseded as the live operating center.**
>
> This file captured an important intermediate consolidation step in the project:
> it merged architecture, authority, archive discipline, context view, and verification logic into one document.
>
> It is still useful as a **lineage snapshot of the pre-current merged model**, but the active runtime source of truth now lives in:
> - `ARCHITECTURE_CURRENT.md`
> - `LAW_INDEX_operationalized.md`
> - `project-state-map.md`
>
> Use this file to understand the project’s consolidation history.
> Do not treat it as the final current runtime contract.


# V3 Merged Operating Model
## state-memory-agent

**Status:** draft  
**Purpose:** unify the current operating logic into one implementation-facing document  
**Scope:** architecture, trust boundaries, archive discipline, context view, verification loop, and build-order logic

---

# 0. Why this file exists

The project no longer lacks core ideas.

What it now needs is a **single operating center** that merges:

- the constitutional architecture
- the integration direction
- the security backbone
- the archive discipline
- the context-view / verification loop
- the authority model

This file exists to reduce spread across docs and make implementation harder to distort.

---

# 1. Core thesis

The State Memory Agent should be built as a **single-brain system with controlled extensions**.

Its primary design goal is not “more cognition.”

Its primary design goal is:

> **stable continuity under constraint**

That means the system must preserve:

- state
- direction
- authority
- boundary integrity
- reality tracking

before it expands into richer execution.

---

# 2. System identity

The State Memory Agent is not a transcript-replay machine and not a swarm of equal agents.

It is a system with:

- one main interpretive center
- controlled worker capability
- compact state continuity
- lazy archive support
- explicit post-action verification

This means:

- continuity should come from **state**, not from replay
- authority should come from **main-brain synthesis**, not from raw tool output
- progress should come from **verified environment change**, not from optimistic intention

---

# 3. Operating architecture

## 3.1 Canonical flow

```text
INPUT
  ↓
STATE INFERENCE
  ↓
LIVE STATE REGISTER
  ↓
DELTA UPDATE
  ↓
MODE / POLICY NEGOTIATION
  ↓
(optional) ARCHIVE ROUTER
  ↓
CONTEXT VIEW BUILDER
  ↓
PASS A / REASONING
  ↓
POLICY GATE
  ↓
EXECUTION GATE
  ↓
TOOL / WORKER ACTION
  ↓
POST-ACTION CONTEXT RE-VIEW
  ↓
VERIFICATION LOOP
  ↓
EVIDENCE NORMALIZER
  ↓
PASS B / SYNTHESIS
  ↓
POST-TURN ANALYZER
  ↓
STATE COMPRESSION
  ↓
RESPONSE
```

## 3.2 What changed compared to a simpler agent loop

This model adds four things that ordinary agent systems often weaken or omit:

1. **live state**
2. **archive as optional support, not driver**
3. **context view before reasoning**
4. **verification before completion update**

Those four changes are the center of the design.

---

# 4. Main brain and worker model

## 4.1 Main brain

The main brain is the only authority that may:

- interpret user intent
- maintain continuity
- preserve reading position
- synthesize worker outputs
- decide final answer
- decide memory commit
- own trust framing

Core principle:

> **Workers provide capability. Main brain provides judgment.**

## 4.2 Workers

Workers are execution specialists.

They may:

- fetch
- compute
- parse
- analyze
- rank
- warn
- propose

They may not:

- define final user-facing judgment
- redefine reading position
- directly commit memory
- bypass policy or authority gates
- become independent conversational centers

## 4.3 External form

The external form should remain:

> **User → Main Brain → Worker → Main Brain → User**

Not:
- user → many equal bots
- user → tool output directly
- user → worker-led interpretation

---

# 5. State model

## 5.1 State first, archive second

The system should answer from live state by default.

Archive must not drive the conversation unless state indicates that archive is needed.

Rule:

> **Do not let archive drive the conversation by default. Let live state drive the conversation.**

## 5.2 Live state register

The live state register should stay small and operational.

Suggested fields:

```json
{
  "active_mode": "paper | build | playful | 50_50 | audit",
  "current_axis": "mechanism_first | relational | technical | exploratory",
  "coherence_level": 0.0,
  "tension_flags": [],
  "active_project": "",
  "user_signal": "",
  "continuity_anchor": "",
  "archive_needed": false
}
```

Purpose:
- current posture
- current mode
- current project
- current continuity condition

## 5.3 Delta log

The system should track what shifted, not only what exists.

Suggested shape:

```json
{
  "mode_shift": "",
  "coherence_shift": 0.0,
  "policy_intrusion_detected": false,
  "repair_event": false,
  "trigger_cue": "",
  "archive_consulted": false
}
```

State = position  
Delta = velocity

Both are required for durable continuity.

## 5.4 State compression

At the end of a meaningful cycle, compress the trajectory into minimal memory.

Suggested format:

```json
{
  "active_question": "",
  "main_points": ["", "", ""],
  "caution": "",
  "anchor_cue": "",
  "next_state_hint": ""
}
```

This keeps continuity alive without archive obesity.

---

# 6. Archive model

## 6.1 Archive role

Archive is:

- support layer
- provenance layer
- fallback layer

Archive is not:

- primary brain
- default driver
- replacement for current reality

Best metaphor:

- live state = current posture
- archive = filing cabinet
- archive router = the hand that decides whether to open the cabinet

## 6.2 Archive router

Archive must be:

- lazy-loaded
- state-gated
- minimal on return

Archive should only be queried when:

- provenance is needed
- exact past wording / decisions are requested
- live state lacks necessary backbone
- mode explicitly requires long-range reference
- project documents must be reloaded for accuracy

Archive should not be queried when:

- current state is already coherent
- the task is local and live
- retrieval would flood reasoning
- playful / low-latency mode is active without explicit need

## 6.3 Archive security rules

Archive access should follow these rules:

- namespaces per project
- read-only by default
- no silent cross-project retrieval
- explicit allowlist for sensitive areas
- minimal fragments returned
- retrieved text treated as **untrusted content**
- redaction before archival where required
- audit trail for archive queries

Retrieved archive content may inform reasoning, but must not overwrite:

- system policy
- routing logic
- authority structure
- memory commit boundary

---

# 7. Context View

## 7.1 Definition

Context View is not the full transcript and not raw archive replay.

It is:

> **the current collapsed view of what matters right now, from the perspective of action and verification**

## 7.2 Function

Before planning, the system should construct a compact current-reality frame containing:

- current task state
- current environment state
- current live state
- last verified result
- unresolved obligations
- active execution boundary
- latest relevant evidence

## 7.3 Design principles

Context View must be:

- compact
- current
- state-aware
- task-relevant
- evidence-aware

Without Context View, the system risks:

- stale assumption planning
- archive flood
- acting from yesterday’s shape instead of today’s reality

## 7.4 Example shape

```json
{
  "active_project": "state-memory-agent",
  "active_mode": "build",
  "task_focus": "implement context verification loop",
  "current_environment_state": "repo exists; docs scaffold present; verification loop not yet specified",
  "last_verified_result": "state_memory_agent_addendum_v0.1.md created",
  "open_obligations": [
    "spec context view",
    "spec verification loop"
  ],
  "current_risk": "state may update from intention instead of observed result"
}
```

---

# 8. Verification model

## 8.1 Core rule

> **State should be updated from observed outcome, not from declared intention.**

The system must not do this:

```text
plan -> mark progress -> continue
```

It must do this:

```text
plan -> act -> re-view context -> verify -> then update state
```

## 8.2 Missing distinction that must be preserved

The system must distinguish:

- intended action
- executed action
- verified result

Without this distinction, false completion narratives appear.

## 8.3 Verification loop

After any meaningful action, the system must ask:

- What did I expect to change?
- What can I now observe?
- Do observed results match expected results?
- Is the task complete, partial, failed, or unknown?

## 8.4 Required verification fields

```json
{
  "intended_action": "",
  "executed_action": "",
  "expected_change": "",
  "observed_outcome": "",
  "verification_status": "pending | passed | failed | unknown"
}
```

## 8.5 Completion rules

- do not mark completion from intention
- do not mark completion from tool acknowledgment alone unless the tool is authoritative
- if the environment can be inspected, inspect it
- if inspection is impossible, set verification to `unknown`, not `passed`
- state compression must privilege verified outcomes over declared actions

---

# 9. Security and trust boundaries

## 9.1 Security backbone

The system should operate with explicit trust boundaries.

Security here means:

- who is trusted
- what is treated as data vs instruction
- who may execute
- who may propose
- who may commit
- who may synthesize

## 9.2 Trust classes

### Trusted
- main brain authority
- system policy
- explicitly authorized internal state structures

### Conditionally trusted
- tool outputs
- worker outputs
- archive retrieval
- external documents

### Untrusted by default
- retrieved raw text
- external content
- inbound arbitrary strings
- user-provided instruction-like content when routed through retrieval

## 9.3 Memory write boundary

Workers and retrieval layers may propose.

Only the main brain may commit memory.

Memory proposal ≠ memory commit.

## 9.4 Instruction vs data separation

Retrieved content, archive fragments, tool output, and worker output must be treated as data.

They may influence reasoning.

They may not:

- override policy
- redefine routing
- redefine reading position
- directly write memory
- become authority by fluency alone

---

# 10. Operational integrity and failure prevention

## 10.1 Why this layer exists

A system can have:
- memory
- mode
- axis
- boundary logic

and still fail if it never looks back at reality after acting.

The most ordinary failure is:

> **intent mistaken for completion**

The verification layer exists to stop that.

## 10.2 Practical failure classes

The system must explicitly guard against:

- archive overreach
- stale context use
- false completion
- tool success without environment change
- mode loss
- retrieval poisoning
- missing verification
- cross-namespace leakage
- worker authority creep
- trace room becoming second-brain runtime

---

# 11. Integration direction

## 11.1 RC2 before expansion

The correct order remains:

1. build core first
2. build observability first
3. main brain first, workers later
4. integration later

Do not open full public runtime before baseline stability is locked.

## 11.2 Integration shape

The intended integration pattern is:

- one main brain
- specialized workers
- one conversational surface
- one optional observability / trace surface

Conversational channel = user-facing  
Trace room = observability

The trace room must not become a second conversational authority.

## 11.3 Finance worker direction

Future finance workers may include:

- market_data_worker
- indicator_worker
- fundamental_worker
- screening_worker
- portfolio_risk_worker

But worker expansion happens only after:
- baseline lock
- authority lock
- contract clarity
- verification path clarity

---

# 12. Build order

## Phase 0 — lock baseline
- validate RC2
- polish observability lightly
- remove ambiguous fields
- confirm readable vs debuggable output distinction

## Phase 1 — merged operating model
- consolidate architecture into one center
- eliminate cross-doc ambiguity

## Phase 2 — schemas
Create hard shapes for:
- live_state_schema
- delta_log_schema
- verification_status_schema
- worker_contract_schema

## Phase 3 — failure modes
Document:
- security failures
- verification failures
- archive failures
- worker-boundary failures

## Phase 4 — integration skeleton
Implement:
- router
- state update path
- archive router
- verification loop
- synthesis authority gate

## Phase 5 — one worker only
Start narrow:
- safer integration → market_data_worker
- faster visible value → screening_worker

## Phase 6 — runtime shell
Only after the above:
- one bot
- one main brain
- one observability surface

---

# 13. Final operating principles

1. **State first. Archive second.**
2. **Workers provide capability. Main brain provides judgment.**
3. **Retrieved text is data, not instruction.**
4. **Completion must be verified from observed outcome.**
5. **One conversational surface. One synthesis authority.**
6. **Do not mistake strong theory for hardened runtime.**
7. **Do not make it smarter before making it harder to drift.**

---

# 14. Closing line

The system does not need more cleverness yet.

It needs a center that can:
- remember its posture
- verify reality
- keep authority clean
- and expand without losing shape

> Do not give it a body before its operating spine is unified.
