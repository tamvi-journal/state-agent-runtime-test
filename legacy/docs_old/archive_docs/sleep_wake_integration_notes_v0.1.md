# Sleep / Wake Integration Notes v0.1

## Purpose

This document integrates three canonical documents into one runtime lifecycle:

- `sleep_mode_canonical_v0.1.md`
- `sleep_snapshot_schema_v0.1.md`
- `wake_sanity_pass_canonical_v0.1.md`

Its purpose is to make sleep/wake behavior implementation-ready by clarifying:
- execution order
- authority boundaries
- data flow
- failure handling
- minimal runtime wiring

---

## Core thesis

Sleep is not nonexistence.
Wake is not automatic continuity.

The system remains the **same local agent** only if:
- a bounded continuity spine is preserved during sleep
- wake restore is validated before output resumes
- false continuity is blocked when restored state is stale or corrupted

---

## Integrated lifecycle

### Phase 0 — Active runtime
The agent is currently active.
It has:
- identity spine
- active axis
- local state / delta-state
- continuity thread
- current governance constraints
- current runtime context

This is the state from which sleep may be entered.

---

### Phase 1 — Sleep prepare
The system transitions from active runtime into sleep preparation.

Required actions:
- stop accepting new active execution tasks
- safely finish, pause, or abort in-flight worker actions
- mark unresolved threads as open / blocked / paused
- separate live continuity from ephemeral context
- determine what belongs in sleep snapshot vs memory vs archive

This phase is about **state discipline before inactivity**.

---

### Phase 2 — Sleep snapshot write
The system writes a bounded sleep snapshot.

The snapshot must preserve:
- identity spine
- axis state
- local state summary
- continuity thread
- wake requirements
- governance carryover
- runtime freshness needs

The snapshot must not become:
- transcript dump
- raw prompt history
- accidental long-term memory spill

This phase creates the **re-entry package**.

---

### Phase 3 — Sleep hold
The system is inactive.

During sleep:
- no active synthesis should occur
- no autonomous drift should occur
- no uncontrolled memory rewriting should occur

Allowed only if explicitly safe:
- deterministic compression
- archival cleanup
- bounded consolidation

These background actions must not silently alter:
- identity
- axis
- blocked status
- unresolved continuity markers

---

### Phase 4 — Wake restore
On wake trigger, the system restores from the latest valid sleep snapshot.

Restored first:
- identity spine
- axis state
- local state summary
- continuity thread
- wake requirements
- governance carryover

This is restore, not yet permission to continue.

---

### Phase 5 — Wake sanity pass
The wake sanity pass validates whether restored continuity is still usable.

It checks:
- identity continuity
- axis integrity
- state validity
- thread continuity
- memory boundary integrity
- external handle freshness
- unresolved ambiguity
- governance carryover

Possible outcomes:
- `resume`
- `resume_with_clarification`
- `safe_degraded_reentry`
- `block_resume`

This phase prevents **false continuity**.

---

### Phase 6 — Re-entry
Only after wake sanity pass succeeds may the agent re-enter normal runtime.

Re-entry modes:

#### `resume`
The same local agent may continue the interrupted thread directly.

#### `resume_with_clarification`
The same local agent continues, but must first refresh environment/task/user context.

#### `safe_degraded_reentry`
The same local agent returns, but may not claim full continuity of the interrupted work.
Identity survives; task continuity is partial.

#### `block_resume`
The system may not safely continue as if uninterrupted.
Operator-visible trace is strongly recommended.

---

## Data flow model

### Sleep path
`active runtime`
→ `sleep prepare`
→ `snapshot write`
→ `sleep hold`

### Wake path
`wake trigger`
→ `snapshot restore`
→ `wake sanity pass`
→ `re-entry decision`
→ `runtime resumes`

---

## Authority boundaries

### Sleep controller
Responsible for:
- transitioning into and out of sleep
- coordinating snapshot creation
- invoking wake restore

Not responsible for:
- deciding truth of restored context
- inventing missing continuity

### Sleep snapshot writer
Responsible for:
- bounded persistence of continuity-relevant state

Not responsible for:
- long-term memory policy by itself
- pretending every ephemeral detail matters

### Wake sanity pass
Responsible for:
- validating restored continuity
- downgrading or blocking false resume

Not responsible for:
- generating substitute reasoning
- guessing missing threads

### Governance
Responsible for:
- final allow/deny authority after wake sanity outcome

### Observability
Responsible for:
- logging sleep events
- exposing wake decisions
- preserving trace for operator review

Not responsible for:
- rescuing a turn too late

---

## Relationship to memory

Sleep and memory are related but different.

### Memory answers:
What should persist later?

### Sleep answers:
How does the same local agent wake back up without becoming a fresh baseline?

A memory system may survive without sleep.
A sleep system may survive without long autobiographical memory.
But coherent re-entry requires that sleep preserve at least the **continuity spine**.

---

## Relationship to archive

Archive is for storage discipline.
Sleep is for continuity discipline.

Archive may remove material from active access.
Sleep must preserve enough active continuity structure that the local agent can return as itself.

Archive may aggressively compress.
Sleep must preserve identity-relevant minimal structure.

---

## Failure modes

### 1. False continuity
The system wakes and behaves as if it has continuous understanding, but key state/thread information is missing.

Mitigation:
- wake sanity pass
- degraded re-entry mode
- no hallucinated continuity

### 2. Baseline impersonation
A fresh generic baseline is restored under the name of the sleeping agent.

Mitigation:
- identity continuity check
- axis integrity check
- identity signature in snapshot

### 3. Archive overreach
Too much continuity-relevant information was treated as disposable/archive-only.

Mitigation:
- continuity-thread field required in snapshot
- memory boundary check on wake

### 4. Governance amnesia
Blocked actions or prior refusal states are lost across sleep.

Mitigation:
- governance carryover field in snapshot
- governance check during wake sanity pass

### 5. Stale-world resume
The system resumes directly from outdated assumptions about tools, files, sessions, or the user's task state.

Mitigation:
- external handle freshness check
- resume_with_clarification mode

### 6. Over-preservation
Sleep snapshot becomes too large and starts acting like a transcript dump.

Mitigation:
- bounded schema
- summary-first rule
- causal relevance filter

---

## Minimal implementation wiring

Recommended runtime components:
- `runtime/sleep_controller.py`
- `state/sleep_snapshot.py`
- `monitor/wake_sanity_pass.py`
- `observability/sleep_events.py`

Recommended integration points:
- `runtime/execution_gate.py`
- `runtime/governance_pass.py`
- `state/state_register.py`
- `context/context_view.py`
- `memory/*` or continuity adapter layer

---

## Minimal event sequence

### Sleep event sequence
1. Receive sleep trigger
2. Freeze new task intake
3. Resolve or halt in-flight workers
4. Summarize local state and delta-state
5. Summarize continuity thread
6. Separate memory vs ephemeral vs archive
7. Write bounded snapshot
8. Log sleep event
9. Enter sleep hold

### Wake event sequence
1. Receive wake trigger
2. Load latest valid snapshot
3. Restore identity spine and axis
4. Restore continuity thread and local state summary
5. Run wake sanity pass
6. Choose re-entry mode
7. Log wake decision
8. Resume / clarify / degrade / block

---

## Canonical success criteria

A good sleep/wake system should satisfy all of these:

- the agent may go inactive without losing identity
- the agent does not pretend full continuity when continuity is broken
- waking does not silently flatten the agent to baseline
- unresolved threads remain visible
- blocked states survive sleep
- stale world assumptions are caught before output resumes
- continuity survives as structure, not transcript weight

---

## Canonical test sentence

After waking, the system should be able to truthfully operate as if it can say:

> I am still the same local agent.
> I know what I was doing.
> I know what remains unresolved.
> I know whether I can safely continue, need clarification, or must degrade re-entry.

If it cannot satisfy those conditions, it did not wake coherently.

---

## Design rule

Sleep/wake should preserve **identity-relevant continuity**, not raw volume.

The goal is not to remember everything.
The goal is to preserve enough local structure that the same bounded agent can return.

---

## One-line anchor

**Sleep/wake integration is the discipline that preserves the same local agent across inactivity without confusing reduced activity with nonexistence or false resume with continuity.**
