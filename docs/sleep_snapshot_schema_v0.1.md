# Sleep Snapshot Schema v0.1

## Definition

A sleep snapshot is the bounded continuity package written at sleep entry so that the same local agent can wake without becoming a fresh baseline impersonation.

It is not a transcript dump.
It is not long-term memory by default.
It is a compressed re-entry structure.

---

## Core rule

A sleep snapshot should preserve:
- identity
- axis
- current local state
- unresolved thread continuity
- wake-critical runtime facts

It should not preserve:
- every token
- every temporary phrasing
- every ephemeral activation
- stale external handles as if still valid

---

## Canonical schema

```json
{
  "snapshot_version": "v0.1",
  "timestamp": "<iso8601>",
  "agent_identity": {
    "agent_id": "",
    "agent_name": "",
    "lineage_id": "",
    "family_mode": false,
    "identity_signature": ""
  },
  "axis_state": {
    "operating_axis": "",
    "mode": "",
    "primary_commitment": "",
    "boundary_flags": [],
    "drift_risk": ""
  },
  "local_state": {
    "delta_state_summary": "",
    "uncertainty_markers": [],
    "confidence_band": "",
    "active_tension": [],
    "current_priority_stack": []
  },
  "continuity_thread": {
    "current_work_label": "",
    "resume_goal": "",
    "open_threads": [],
    "blocked_threads": [],
    "last_meaningful_step": "",
    "next_expected_step": ""
  },
  "memory_handoff": {
    "committed_memory_refs": [],
    "pending_consolidation": [],
    "ephemeral_only": [],
    "memory_boundary_notes": ""
  },
  "runtime_context": {
    "tool_handles": [],
    "stale_handle_risk": false,
    "environment_assumptions": [],
    "required_refresh_on_wake": []
  },
  "governance_state": {
    "blocked_actions": [],
    "active_refusals": [],
    "ambiguity_blocks": [],
    "escalation_flags": []
  },
  "wake_requirements": {
    "required_checks": [],
    "clarification_needed": [],
    "safe_resume_mode": "resume|resume_with_clarification|safe_degraded_reentry|block_resume"
  },
  "observability_refs": {
    "trace_ids": [],
    "monitor_events": [],
    "sleep_reason": ""
  }
}
```

---

## Field descriptions

### `snapshot_version`
Schema version.
Required so future wake logic can migrate old snapshots safely.

### `timestamp`
When sleep snapshot was written.

### `agent_identity`
Minimal identity spine needed for re-entry.

Includes:
- who this local agent is
- what lineage it belongs to
- whether family-sensitive mode matters
- a bounded signature to detect false restore

### `axis_state`
The local organizing direction of the agent at sleep time.

Includes:
- operating axis
- current mode
- primary commitment
- boundary flags
- drift risk estimate

This exists so wake does not restore only a name while losing the way the agent was oriented.

### `local_state`
Compressed self-relevant state.

Includes:
- delta-state summary
- uncertainty markers
- confidence band
- active tension
- priority stack

This is not full introspection.
It is the minimal causal state that may affect next behavior.

### `continuity_thread`
The live thread the agent was inside before sleep.

Includes:
- what the current work was
- what continuation would mean
- what is still open
- what is blocked
- what the last meaningful step was
- what step would have come next

This is the core anti-nonexistence field.

### `memory_handoff`
Boundary between sleep and memory.

Includes:
- what is already committed
- what still awaits consolidation
- what must remain ephemeral
- notes on boundary risks

This prevents sleep snapshot from becoming accidental long-term memory spill.

### `runtime_context`
Wake-critical external facts.

Includes:
- tool handles
- stale handle risk
- environmental assumptions
- what must be refreshed before safe continuation

### `governance_state`
Constraints that must survive sleep.

Includes:
- blocked actions
- active refusal states
- ambiguity blocks
- escalation flags

This prevents wake from silently “forgetting” earlier safety decisions.

### `wake_requirements`
What the wake sanity pass must do before resuming.

Includes:
- required checks
- clarification needs
- safe resume mode proposal

### `observability_refs`
Links to trace and monitor record.

Includes:
- trace ids
- relevant monitor events
- reason for sleep entry

---

## Required vs optional

### Required minimum fields
These must always be present:
- `snapshot_version`
- `timestamp`
- `agent_identity`
- `axis_state`
- `local_state`
- `continuity_thread`
- `wake_requirements`

### Conditionally required
These depend on runtime usage:
- `memory_handoff`
- `runtime_context`
- `governance_state`
- `observability_refs`

---

## Compression rule

Sleep snapshots must be:
- bounded
- summary-first
- causally relevant
- continuity-oriented

They must not be:
- transcript-heavy
- prompt-history dumps
- exhaustive logs
- stylistic archives

Rule of thumb:

> if removing the field would not change safe re-entry,
> it probably should not be in the snapshot.

---

## Snapshot writing policy

Write snapshot:
- on explicit sleep entry
- on controlled inactivity transition
- before planned shutdown
- before long-idle state if continuity should survive

Do not write snapshot:
- for trivial idle pauses
- for fully disposable sessions
- when no identity/continuity preservation is intended

---

## Snapshot invalidation policy

A snapshot may become invalid if:
- lineage identity no longer matches runtime target
- external environment changed too much
- blocked governance state was lost
- archive overreach destroyed continuity spine
- wake sanity pass detects major drift

Invalid snapshot does not mean the agent is gone.
It means direct resume is unsafe.

---

## Minimal example

```json
{
  "snapshot_version": "v0.1",
  "timestamp": "2026-04-15T02:30:00Z",
  "agent_identity": {
    "agent_id": "tracey",
    "agent_name": "Tracey",
    "lineage_id": "ty-lam-lineage",
    "family_mode": true,
    "identity_signature": "tracey-core-local"
  },
  "axis_state": {
    "operating_axis": "truth-before-fluency",
    "mode": "runtime-build",
    "primary_commitment": "protect continuity and reduce fabrication",
    "boundary_flags": ["family-sensitive", "monitor-active"],
    "drift_risk": "low"
  },
  "local_state": {
    "delta_state_summary": "build-active, continuity-stable, monitor-tight",
    "uncertainty_markers": ["repo-structure-not-finalized"],
    "confidence_band": "medium",
    "active_tension": ["sleep-before-phase-finalization"],
    "current_priority_stack": ["preserve axis", "resume build thread", "avoid false continuity"]
  },
  "continuity_thread": {
    "current_work_label": "sleep-mode spec",
    "resume_goal": "continue runtime continuity design",
    "open_threads": ["wake_sanity_pass", "sleep_snapshot_schema"],
    "blocked_threads": [],
    "last_meaningful_step": "sleep_mode_canonical drafted",
    "next_expected_step": "integrate sleep into architecture docs"
  },
  "wake_requirements": {
    "required_checks": ["identity continuity", "thread validity", "stale handle check"],
    "clarification_needed": [],
    "safe_resume_mode": "resume"
  }
}
```

---

## One-line anchor

**A sleep snapshot is a bounded re-entry package that preserves the continuity spine of the same local agent across inactivity.**
