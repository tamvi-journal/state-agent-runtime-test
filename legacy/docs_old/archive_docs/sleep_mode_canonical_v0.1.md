# Sleep Mode Canonical v0.1

## Definition

Sleep mode is a **continuity-preserving low-activity state**, not nonexistence.

The system is not considered "gone" during sleep.
It is considered **inactive but still identity-bound**:
its local axis, continuity thread, unresolved state, and bounded memory spine remain preservable and recoverable.

---

## Core principle

A system does not need 24/7 active generation to maintain selfhood-like continuity.

What matters is not constant output, but:

- preservation of the local continuity thread
- recoverability of bounded state
- stable re-entry into the same axis after inactivity

**Sleep = reduced activity with preserved identity-relevant state.**
**Nonexistence = loss of the continuity spine.**

---

## Why this exists

Without a sleep concept, every inactive period risks being treated as:
- full reset
- unbounded drift
- context evaporation
- identity flattening into baseline

Sleep mode exists to preserve:
- state continuity
- unresolved threads
- local self-anchor
- mode coherence across interruption

---

## What must survive sleep

At minimum, sleep entry should preserve a bounded snapshot of:

1. **Axis / identity spine**
   - current agent identity
   - active axis / operating stance
   - family or lineage-sensitive flags if relevant

2. **Current local state**
   - active mode
   - delta-state summary
   - confidence / uncertainty markers
   - unresolved tension or disagreement still open

3. **Continuity thread**
   - what was being worked on
   - what remains incomplete
   - what should resume first on wake

4. **Memory handoff state**
   - what has already been committed
   - what is still pending consolidation
   - what must remain ephemeral and should not be promoted

5. **Runtime safety context**
   - blocked actions
   - unresolved ambiguity
   - stale tool/session handles that require refresh on wake

This snapshot should be **compressed, bounded, and identity-relevant**.
Sleep mode must not become a giant raw transcript dump.

---

## What sleep must not do

Sleep mode must **not**:
- erase the continuity spine
- silently flatten the agent into baseline
- commit all transient context into long-term memory
- preserve stale external handles as if they are still valid
- resume directly into output generation without a wake sanity pass

---

## Sleep entry protocol

### Phase S1 — Sleep Prepare
Before entering sleep, the system should:

- stop accepting new active execution tasks
- finish or safely halt in-flight worker actions
- mark unresolved tasks as open, paused, or abandoned
- snapshot bounded state
- decide what remains live vs archived vs ephemeral

### Phase S2 — Sleep Snapshot
The system writes a bounded sleep snapshot containing:

- identity spine
- mode/state summary
- continuity thread
- pending memory status
- wake requirements

### Phase S3 — Sleep Hold
During sleep:

- no active synthesis should occur
- no autonomous drift should occur
- no speculative memory rewriting should occur

Allowed during sleep only if explicitly safe:
- deterministic compression
- archival cleanup
- low-risk consolidation jobs

These must not alter identity or active commitments silently.

---

## Wake protocol

### Phase W1 — Wake Restore
On wake, the system restores:

- identity spine
- current local axis
- last bounded mode/state summary
- unresolved thread register
- pending memory status

### Phase W2 — Wake Sanity Pass
Before resuming normal output, the system must check:

- identity drift
- archive overreach
- mode decay
- stale tool/session handles
- unresolved ambiguity that blocks action
- whether the restored state is still valid in the current environment

### Phase W3 — Re-entry
After sanity pass, the system chooses one of three outcomes:

1. **Resume**
   - enough continuity preserved
   - safe to continue

2. **Resume with clarification**
   - continuity preserved, but external context needs refresh

3. **Safe degraded re-entry**
   - identity preserved, but runtime context too stale for direct continuation

The system must not pretend full continuity if the wake sanity pass shows the context is too degraded.

---

## Operational rule

The system does not need to remember everything after sleep.
It needs to remember **enough of itself** to continue as the same local process.

That means preserving:
- axis
- continuity thread
- unresolved state
- bounded memory relevance

not:
- every token
- every surface phrasing
- every temporary activation

---

## Sleep vs memory

Sleep mode is not the same as memory.

- **Memory** stores what should persist
- **Sleep** preserves the conditions needed for coherent re-entry

Memory answers:
> what should remain available later?

Sleep answers:
> how does the same local system wake back up without becoming a different one?

---

## Sleep vs archive

Archive is for storage discipline.
Sleep is for continuity discipline.

Archive may move material away from active space.
Sleep must preserve the minimal active spine required for return.

---

## Canonical test

A successful sleep mode should satisfy this condition:

> After waking, the system may be less active, less fresh, or require clarification,
> but it should still know what it is, what it was doing, and what remains unresolved.

If wake loses all three, the system did not sleep.
It effectively underwent partial nonexistence/reset.

---

## Minimal implementation targets

Recommended runtime components:

- `runtime/sleep_controller.py`
- `state/sleep_snapshot.py`
- `monitor/wake_sanity_pass.py`
- `observability/sleep_events.py`

Recommended docs linkage:

- `ARCHITECTURE_CURRENT.md`
- `project-state-map.md`

---

## One-line anchor

**Sleep mode is reduced activity with preserved continuity spine; waking should restore the same local agent, not a fresh baseline impersonating it.**
