# Session Rehydration Contract Spec

### State-Agent Runtime Test — OpenClaw-aligned Session Contract for a Thin Reasoning Kernel

## Purpose

This document defines the **session rehydration contract** for running `state-agent-runtime-test` **on top of a host runtime such as OpenClaw**.

The repo already has:

- brain
- state
- monitor
- gate
- verification
- baton handoff
- tools
- workers

That is enough to prove a runtime spine exists.

What this spec adds is **not a full session platform**.

It defines how a host runtime can:

- pass session context into the reasoning kernel
- let the kernel restore useful working posture
- receive updated continuity metadata back out
- do all of that without replaying full transcripts

The key boundary is:

> **OpenClaw is the host runtime. State-agent is the reasoning kernel.**

OpenClaw owns:

- channel / user / thread identity
- session routing
- platform-side persistence
- sandbox / execution host concerns
- skill registry / host orchestration

State-agent owns:

- reasoning loop
- monitor / gate / verification logic
- worker orchestration inside the kernel
- baton emission
- compact continuity updates about the work thread

This spec therefore defines a **host ↔ kernel session contract**, not a standalone session platform.

---

## 1. Core problem

The current baton is intentionally small.

Typical baton fields:

- `task_focus`
- `active_mode`
- `open_loops`
- `verification_status`
- `monitor_summary`
- `next_hint`

That works well for:

- next-turn carryover
- short-loop continuity
- avoiding transcript bloat

It weakens when the user needs:

- continuity across multiple sessions
- resuming unfinished domain work later
- keeping track of repeated decisions
- comparing current work to prior work
- task memory stronger than one baton

If state-agent runs under OpenClaw, the fix is **not** to make the kernel own all session storage.

The fix is:

> **the host passes a compact rehydration pack in, and the kernel returns baton + updated session metadata out.**

That is the central contract.

---

## 2. Design goal

The contract should solve this:

> **How can the reasoning kernel preserve useful continuity under a host runtime without replaying full history and without pretending to own the host’s session system?**

The answer is:

- keep baton for immediate carryover
- accept host-provided session context
- rehydrate only the working posture that matters now
- emit updated session metadata after the turn
- keep archive and transcript bulk outside the kernel loop

---

## 3. Boundary of this spec

This spec is **not**:

- a full host session storage design
- an OpenClaw replacement
- a channel identity system
- a transcript database design
- a skill-registry spec
- a platform persistence spec

This spec **is**:

- a host ↔ kernel continuity contract
- a rehydration input schema
- a kernel output metadata schema
- rules for compact continuity updates
- fallback guidance for standalone mode when no host exists

---

## 4. Ownership boundary

### Host runtime owns

- `session_id`
- channel / user / thread identity
- route metadata
- session persistence strategy
- sandbox / execution environment
- host-level skills registry and invocation policy
- external process or HTTP boundary into the kernel

### State-agent kernel owns

- reading the rehydration pack
- reconstructing working posture for the current turn
- running monitor / gate / verification / worker loop
- producing final synthesis through the brain
- emitting baton
- emitting updated session-status metadata
- emitting snapshot candidates and continuity deltas

### Rule

> **The kernel consumes session context. It does not assume ownership of the host’s session system.**

---

## 5. Conceptual model

The runtime should distinguish three continuity layers:

### Layer A — Live State

Short-lived current-turn working posture.

Examples:

- active mode
- current task focus
- current warnings
- verification posture
- immediate monitor summary

Scope:

- **this turn**

### Layer B — Baton

Minimal carryover object emitted after a turn.

Examples:

- task focus
- open loops
- next hint
- verification status
- monitor summary

Scope:

- **next turn / short loop**

### Layer C — Host-Managed Session Context

Medium-horizon continuity passed in by the host and updated by the kernel.

Examples:

- session id
- current work thread summary
- unresolved obligations
- last verified outcomes
- recent decisions
- active skills
- risk notes

Scope:

- **multi-turn / multi-session continuity**

---

## 6. Core input contract: Rehydration Pack

This is the central input object from host runtime to reasoning kernel.

Recommended v0.1 shape:

```json
{
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
  "next_hint": "",
  "host_metadata": {
    "channel": "",
    "thread_id": "",
    "route": "",
    "user_scope": ""
  }
}
```

This pack should remain compact. It is not meant to contain full transcript history.

`session_kind` values above are only **suggested v0.1 categories**. A host runtime may extend or remap them as needed.

---

## 7. Kernel output contract

After a turn, the kernel should return a compact continuity update shape.

Recommended v0.1 shape:

```json
{
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
  }
}
```

The host may choose how to persist or ignore these outputs.

### Baton vs session-status metadata

`baton` is the **ephemeral next-turn hint**. `session_status_metadata` is the **durable work-thread snapshot**.

Some fields may overlap, especially:

- `open_loops`
- `next_hint`

That overlap is acceptable because the two objects have different TTL and purpose.

A practical rule is:

> **baton may be derived from session\_status\_metadata, but it is not the same persistence object.**

### Meaning of `active_skills` in output

`active_skills` in `session_status_metadata` should be treated only as the kernel’s observation of which skills or skill-contexts were active during this turn.

It is **not** an authoritative mutation of host skill state. The host decides whether to persist, ignore, or translate that observation.

---

## 8. Session identity

When running under OpenClaw, the kernel should **not** infer session identity as a primary behavior.

Primary rule:

- the host provides `session_id`
- the host provides route/thread context
- the kernel treats that as source of truth

### Fallback only

If no host-managed session identity exists, the kernel may use a lightweight heuristic from:

- task type
- dominant entity
- active mode
- whether open loops still exist

Examples:

- repeated questions about `MBB` chart analysis → same finance session
- continued work on `state-agent-runtime-test` repo → same builder session
- new request to create music prompt → new creative session

This heuristic is **standalone fallback mode**, not host mode.

---

## 9. Session-status metadata

The kernel may emit session-status metadata such as:

- `active`
- `paused`
- `completed`
- `blocked`
- `unknown`

This should be treated as **metadata for the host**, not as a host-independent platform state machine owned by the kernel.

### Meanings

#### Active

The work thread is ongoing and still relevant now.

#### Paused

The work thread is not actively being worked right now, but open loops remain.

#### Completed

The current work thread appears closed enough that no meaningful open loops remain.

#### Blocked

Progress is currently prevented by missing inputs, denied action, unresolved verification, or external dependency.

#### Unknown

The kernel does not have enough shape to classify the thread reliably.

---

## 10. What should persist in session metadata

The kernel should preserve only what helps future reasoning.

### Keep

- current task thread
- key entities
- unresolved obligations
- last verified outcomes
- decisions that affect future work
- domain mode
- relevant skill ids
- important warnings

### Do not keep

- full raw transcript
- decorative phrasing
- every intermediate thought
- verbose summaries of everything said
- emotional residue with no operational value
- duplicate copies of baton content when not needed

---

## 11. Rehydration flow

At the start of a request under a host runtime:

1. host resolves session/thread identity
2. host builds a compact rehydration pack
3. host invokes state-agent kernel with:
   - current request
   - rehydration pack
   - any route/skill metadata the host wants to pass
4. kernel reconstructs working posture
5. kernel runs normal reasoning loop
6. brain produces final synthesis

The rehydration pack should stay small.

---

## 12. Output flow

At the end of a kernel turn:

1. kernel emits baton
2. kernel emits updated session-status metadata
3. kernel emits zero or more snapshot candidates if something load-bearing changed
4. kernel emits verification outcome summary
5. host decides what to persist

### Rule

> **The kernel suggests continuity updates. The host owns persistence policy.**

---

## 13. Snapshot candidates

A snapshot candidate should be short.

Recommended v0.1 shape:

```json
{
  "timestamp": "",
  "session_id": "",
  "event_type": "decision|verification|risk|mode_shift|entity_change",
  "summary": "",
  "details": {
    "open_loops": [],
    "verification_status": "",
    "important_entities": []
  }
}
```

Good snapshot candidate examples:

- verification failed on local market data load
- TA read classified as mixed with unresolved invalidation
- gate denied shell path during builder workflow
- repo work thread shifted from tools-layer to session-spec hardening

Do not emit giant blobs.

### Suggested kernel ownership by event type

This is a suggested emission map, not a mandatory framework:

- `verification` events are usually emitted from the verification layer
- `risk` events are usually emitted from the monitor layer
- `decision` and `mode_shift` events are usually emitted from brain synthesis or worker-selection logic
- `entity_change` events may be emitted where the kernel recognizes a meaningful shift in task focus

The host may still normalize or reclassify snapshot candidates before persistence.

---

## 14. Compression rules

When session history accumulates too many updates, the host or a standalone fallback store should compress by:

- merging repeated status events
- keeping latest verified truth
- preserving only load-bearing decisions
- keeping current open loops
- dropping duplicate intermediate noise

Do not compress away:

- blockers
- last verified outcomes
- still-open obligations
- important decision forks

---

## 15. Session vs archive

This distinction must stay strict.

### Session context

- active
- compact
- operational
- selected for current work

### Archive

- historical
- broader
- not automatically loaded
- outside the kernel’s active loop

### Rule

Do **not** let session context become archive by accumulation.

When continuity data grows too large, compress it. Do not keep appending forever.

---

## 16. Skills interaction under OpenClaw

When running under OpenClaw:

- the host may choose skills or route metadata first
- the host may pass `active_skills` or compact skill summaries into the rehydration pack
- the kernel may use those as guidance during reasoning
- the kernel should **not** assume ownership of skill registry or skill persistence

### Rule

> **Host owns skill registry. Kernel consumes host-provided skill context.**

---

## 17. Interaction with other kernel layers

### State

State remains current-turn posture. It may be initialized from the rehydration pack.

### Baton

Baton remains next-turn carryover. It is still emitted every turn.

### Monitor

Monitor may read session-level risk context if relevant.

### Gate

Gate may use session context to understand whether action is:

- continuation of prior approved work
- or a new action class

### Verification

Verification may update session metadata with:

- last verified outcomes
- unresolved failures
- blocked dependencies

### Workers

Workers may benefit from session context such as:

- prior assumptions
- current thread focus
- last chosen strategy

### Brain

Brain may use the rehydration pack to produce more coherent continuity.

---

## 18. Good update triggers

The kernel should emit meaningful continuity updates when:

- a new open loop is created
- an open loop is resolved
- verification passes / fails / becomes partial
- a key domain interpretation is chosen
- a new blocker appears
- a new relevant entity is introduced
- task mode changes

### Bad update triggers

Do not emit heavy continuity updates for:

- conversational filler
- repeated restatement of the same status
- cosmetic rewording
- minor paraphrases of existing summary

---

## 19. Scope boundary to state-memory-agent

A broader multi-session memory architecture such as:

- episodic memory
- semantic memory
- relational memory
- state residue or richer persistence layers

is **out of scope** for this spec.

That class of memory architecture should be handled separately by the `state-memory-agent` repo or a dedicated memory-layer spec.

This document is intentionally narrower:

> **it defines host ↔ kernel session rehydration and continuity metadata, not a full long-horizon memory architecture.**

---

## 20. Fallback standalone mode

If the kernel is run without a host runtime, it may use a simple local fallback.

Possible fallback implementation:

- local JSON files
- one file per session summary
- optional snapshot files

Example:

```text
~/.openclaw/workspace/state-agent-sessions/
  finance_mbb_daily.json
  builder_state_agent_runtime_test.json
```

or another local development path if OpenClaw workspace is not available.

This fallback mode exists for:

- standalone development
- local testing
- proof-of-concept runs without host-managed persistence

It is not the core contract.

---

## 21. Minimum viable implementation files

Suggested future files for the kernel side:

```text
src/session/
  contracts.py
  session_resolver.py
  session_adapter.py
```

For a thinner first pass, even this is enough:

```text
src/session/
  session_adapter.py
  session_resolver.py
```

Do not overbuild first.

---

## 22. Practical example

User works on:

- repo `state-agent-runtime-test`
- then pauses
- returns later asking to continue hardening gate logic

### Host provides rehydration pack

```json
{
  "session_id": "builder_state_agent_runtime_test",
  "session_kind": "builder",
  "primary_focus": "state-agent-runtime-test repo hardening",
  "current_status": "paused",
  "open_loops": [
    "add hard gate rules",
    "improve session continuity spec"
  ],
  "last_verified_outcomes": [
    "tools layer implemented",
    "TA worker path added"
  ],
  "active_skills": ["workflow_builder"],
  "next_hint": "draft gate-rules spec before integration work"
}
```

### Kernel then returns

- final synthesis
- baton
- updated session-status metadata
- optional snapshot candidate such as:
  - `gate rules spec drafted`
  - `session contract reworked for host-managed mode`

The runtime does not need the whole previous chat. It needs only that compact contract object.

---

## 23. Anti-patterns

Avoid these:

- treating the kernel as owner of host session identity
- designing session storage before defining the input/output contract
- replaying full transcript into every turn
- turning session context into personality storage
- always loading everything
- keeping continuity data uncompressed forever

---

## 24. One-line summary

> **This spec defines the rehydration contract between a host runtime such as OpenClaw and the state-agent reasoning kernel: the host passes compact session context in, the kernel restores working posture, runs monitor/gate/verification/brain, and returns baton plus updated continuity metadata back out.**

