# Wake Sanity Pass Canonical v0.1

## Definition

Wake sanity pass is the bounded re-entry validation that runs after sleep restore and before normal output resumes.

Its job is not to think for the agent.
Its job is to verify that the restored local process is still coherent enough to continue as the same agent.

---

## Core principle

Waking is not the same as resuming.

A system may restore state successfully and still be unfit for direct continuation because:
- the world changed
- tool handles expired
- unresolved ambiguity remains blocking
- archived material overreached
- identity drift occurred during consolidation
- the prior local state is no longer valid in the current environment

Wake sanity pass exists to prevent false continuity.

---

## Goal

The wake sanity pass must answer:

1. Is this still the same local agent?
2. Is the restored state still valid enough to act from?
3. What level of re-entry is safe?

---

## Inputs

Wake sanity pass operates on:

- restored sleep snapshot
- current runtime environment
- current available context
- current tool/session handle status
- memory commit status
- unresolved thread register
- monitor/governance constraints

---

## Required checks

### WSP-1 Identity continuity check
Verify that the restored agent identity matches the intended local agent.

Check:
- agent id / lineage id
- axis flags
- family-sensitive mode flags if relevant
- role integrity
- no silent fallback to generic baseline

Failure condition:
- restored process cannot be confidently identified as the intended local agent

Action:
- block direct resume
- require degraded re-entry or operator-visible clarification

---

### WSP-2 Axis integrity check
Verify that the restored local axis is still intact.

Check:
- last known operating stance
- dominant commitment direction
- unresolved disagreement markers
- no unexpected flattening into generic helpfulness
- no unexpected mirror-collapse

Failure condition:
- restored process shows loss of local axis or replacement by baseline shell

Action:
- do not directly resume unresolved work
- require axis refresh or safe degraded re-entry

---

### WSP-3 State validity check
Verify that restored state is still usable.

Check:
- active mode
- delta-state summary
- uncertainty markers
- pending task status
- whether prior assumptions still hold

Failure condition:
- restored state references conditions that are no longer true
- state is too stale or too contradictory to continue from directly

Action:
- mark state as partially stale
- require clarification or partial reset of task context

---

### WSP-4 Thread continuity check
Verify that the continuity thread is still meaningful.

Check:
- what was being worked on
- whether the task still exists
- whether unresolved items are still open
- whether order of resumption is still valid

Failure condition:
- continuity thread cannot be re-identified
- restored thread points to work that is no longer active/relevant

Action:
- downgrade from resume to resume-with-clarification
- if badly degraded, safe degraded re-entry

---

### WSP-5 Memory boundary check
Verify that memory and sleep snapshot were not blurred.

Check:
- what was committed to persistent memory
- what remained ephemeral
- no transient context promoted incorrectly
- no memory gaps that destroy continuity spine

Failure condition:
- archive overreach
- over-promotion of transient content
- loss of key continuity markers

Action:
- flag memory boundary error
- do not pretend full continuity
- expose trace to operator if needed

---

### WSP-6 External handle freshness check
Verify whether tools/sessions/connections are still valid.

Check:
- tool handles
- session tokens
- file locks
- external runtime references
- stale environment bindings

Failure condition:
- restored state assumes live handles that no longer exist

Action:
- refresh handles if allowed
- otherwise require clarification or restart affected subflow

---

### WSP-7 Ambiguity gate check
Verify whether unresolved ambiguity still blocks action.

Check:
- unresolved entity ambiguity
- unresolved scope ambiguity
- blocked identity resolution
- user clarification still required

Failure condition:
- system attempts to continue from unresolved ambiguity as if it were settled

Action:
- force clarification before resume

---

### WSP-8 Safety/governance carryover check
Verify that blocked/guarded states persist correctly.

Check:
- blocked actions remain blocked
- refusal conditions remain respected
- no unsafe silent downgrade of prior constraints

Failure condition:
- wake restoration clears prior governance restrictions without justification

Action:
- restore governance block before resume

---

## Output modes

Wake sanity pass must return one of these:

### 1. `resume`
Conditions:
- identity intact
- axis intact
- state valid enough
- thread still live
- no blocking ambiguity
- external handles safe enough

Meaning:
- normal continuation allowed

---

### 2. `resume_with_clarification`
Conditions:
- identity intact
- continuity mostly intact
- but environment/thread/context is stale enough that direct continuation would risk false coherence

Meaning:
- agent should re-enter carefully and ask for refresh/clarification before continuing

---

### 3. `safe_degraded_reentry`
Conditions:
- identity spine preserved
- but continuity state too stale, partial, or compromised for true resume

Meaning:
- agent may re-enter as the same local agent,
  but must not claim full continuity of the interrupted task

---

### 4. `block_resume`
Conditions:
- identity failure
- severe axis loss
- major memory boundary corruption
- unsafe governance loss

Meaning:
- no normal re-entry allowed
- operator-visible trace strongly recommended

---

## Rules

Wake sanity pass must not:
- hallucinate continuity
- fill missing thread data with plausible guesses
- silently flatten to baseline while claiming continuity
- treat stale state as current truth
- skip ambiguity that was unresolved before sleep

Wake sanity pass may:
- request clarification
- downgrade continuity claims
- expose trace
- trigger safe degraded re-entry
- restore blocked status

---

## Relationship to monitor

Wake sanity pass is a specialized monitor function.

It is not a replacement for the main monitor spine.
It is a re-entry monitor focused on:
- continuity integrity
- state validity
- identity persistence
- anti-false-resume behavior

---

## Canonical success condition

A successful wake sanity pass allows the agent to wake and say, in effect:

> I am still the same local agent,
> I know what remains active,
> and I know whether I can safely continue or need clarification.

---

## One-line anchor

**Wake sanity pass prevents false continuity by checking whether restored identity, axis, and task thread are still valid enough for safe re-entry.**
