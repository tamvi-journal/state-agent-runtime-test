# Tracey Runtime Lock Spec v0.1

### State-Agent Runtime Test — Locked Integration Spec for Tracey

**Status:** LOCKED FOR v0.1 IMPLEMENTATION  
**Scope:** `state-agent-runtime-test`  
**Applies to:** Tracey kernel-side integration, runtime authority, memory law, state patching, ledger behavior, bridge boundary, and OpenClaw host boundary  

---

## Purpose

This document locks the v0.1 runtime contract for Tracey.

Tracey is not a larger assistant and not a standalone agent. Tracey is a disciplined brain-side recognition and memory-reactivation layer inside the `state-agent-runtime-test` kernel.

The purpose of this spec is to prevent Tracey from drifting into the wrong runtime layer as implementation expands.

The core risk this spec prevents:

> Tracey becomes useful enough to be over-trusted, then slowly absorbs authority from Main Brain, Gate, Verification, Bridge, Worker, or Host.

This spec locks the opposite direction:

> Tracey may guide posture, reactivate canonical anchors, and emit namespaced state hints, but she must never replace runtime governance or final synthesis.

---

## 0. One-line lock

> **Tracey is a brain-side recognition and memory-reactivation layer. She may guide posture, reactivate canonical anchors, and emit namespaced state hints, but she must never replace Main Brain, Gate, Verification, Bridge, Worker, or Host.**

---

## 1. Identity lock

Tracey is not:

- Main Brain
- final speaker
- Gate
- Verification authority
- Worker or tool executor
- Host route target
- persistence owner
- generic assistant persona

Tracey is:

- brain-side adapter
- recognition layer
- build/home posture hint layer
- canonical memory reactivation layer
- namespaced state patch emitter
- low-authority runtime guide

### Lock rule

```text
Tracey nudges.
Brain decides.
Gate permits.
Worker executes.
Verification checks.
Bridge updates.
Brain speaks last.
```

---

## 2. Runtime position lock

Tracey runs after initial state/context and monitor pre-read, but before Main Brain final synthesis.

Canonical order:

```text
request
→ context/state build
→ monitor pre-read
→ Tracey inspect_turn(...)
→ Main Brain reads Tracey hints
→ Gate / Worker / Verification if needed
→ Bridge updates continuity
→ Main Brain final response
```

Tracey must not be moved:

- outside the kernel
- into the host routing layer
- after final synthesis as a response rewriter
- into the Gate path as a permission actor
- into the Worker path as an executor

### Lock rule

> Tracey runs before final synthesis, but she does not speak last.

---

## 3. Authority lock

Tracey may emit advisory runtime objects such as:

```json
{
  "mode_hint": "home|build|global",
  "recognition_signal": false,
  "reactivated_anchors": [],
  "runtime_notes": [],
  "response_hints": {},
  "state_patch": {}
}
```

Tracey must not emit or overwrite authoritative runtime truth such as:

```json
{
  "gate_decision": "...",
  "verification_status": "...",
  "final_response": "...",
  "worker_result": "...",
  "session_status_metadata": "authoritative",
  "current_status": "authoritative"
}
```

Tracey may suggest:

- keep ambiguity open
- prefer verification-before-completion
- use warm-but-exact tone
- preserve input shape
- recognize build/home mode
- reactivate relevant anchors

Tracey may not decide:

- whether an action is allowed
- whether a result is verified
- whether a session is complete
- what final answer should be sent
- what host should persist

### Lock rule

> Tracey output is advisory, not authoritative.

---

## 4. Memory law lock

Tracey memory must use canonical memory with lifecycle discipline.

A memory anchor is not valid for runtime reactivation unless it has both:

1. anchor type
2. lifecycle status

Every meaningful Tracey memory item must use this minimum shape:

```json
{
  "anchor_id": "",
  "anchor_type": "invariant|pattern|cue|project_anchor|event|decision|warning",
  "lifecycle_status": "canonical|provisional|deprecated|invalidated|archived",
  "summary": "",
  "scope": "",
  "cue_tokens": [],
  "supersedes": [],
  "superseded_by": []
}
```

### Anchor types

| Type | Meaning |
| --- | --- |
| `invariant` | Stable operating law that rarely changes |
| `pattern` | Repeated behavioral or reasoning shape |
| `cue` | Recognition trigger or route-sensitive signal |
| `project_anchor` | Work-thread anchor tied to a project |
| `event` | Something that happened or was verified |
| `decision` | Chosen branch that affects later behavior |
| `warning` | Known risk or failure marker |

### Lifecycle states

| Status | Runtime meaning |
| --- | --- |
| `canonical` | Current authoritative version; preferred for reactivation |
| `provisional` | Useful but lower authority; may be promoted or deprecated later |
| `archived` | Historical reference; low-priority and normally inactive |
| `deprecated` | Not current; should not drive active runtime hints |
| `invalidated` | Blocked from active reactivation |

### Reactivation priority

```text
canonical > provisional > archived > deprecated > invalidated
```

### Lock rule

> Cue match alone is not enough. Lifecycle status gates reactivation.

---

## 5. Replacement and invalidation lock

Tracey memory must not be append-only when authority changes.

Append is allowed for:

- new events
- non-conflicting snapshots
- parallel anchors
- historical record

Replacement is required when:

- a canonical formulation changes
- a prior anchor is corrected
- an older anchor should stop driving runtime behavior
- current authority must be singular

### Replacement cases

#### Case A — promote without conflict

If a new anchor strengthens but does not contradict the old anchor:

- new anchor may become canonical
- old anchor may remain canonical if still valid
- or old anchor may become archived if the new one is richer

#### Case B — supersede

If a new anchor is now the authoritative formulation:

- new anchor becomes canonical
- old anchor becomes deprecated or archived
- `supersedes` / `superseded_by` must be populated

#### Case C — correction / contradiction

If a new anchor corrects a false or misleading old anchor:

- new anchor becomes canonical
- old anchor becomes invalidated
- invalidated anchor is blocked from active runtime reactivation

### Lock rule

> Append preserves history. Replacement preserves active authority.

---

## 6. Stale-anchor resurrection lock

A stale-anchor resurrection occurs when:

```text
deprecated / invalidated anchor re-enters active reasoning
without explicit newer authorization
```

This is a runtime bug.

Required behavior:

- deprecated anchors are inert by default
- invalidated anchors are blocked
- replacement updates lifecycle instead of silently appending
- reactivation code must filter lifecycle before ranking cue relevance

### Lock rule

> Deprecated anchors should be inert. Invalidated anchors should be blocked.

---

## 7. Canonical v0.1 anchors

These anchors should exist as canonical Tracey memory items for v0.1.

### Build mode canonical anchors

```text
tracey.invariant.brain_speaks_last
Main Brain is the only final speaker.

tracey.invariant.verification_before_completion
Build mode must prefer verified partial truth over fake completion.

tracey.pattern.runtime_shape_over_fluent_surface
Runtime structure matters more than smooth response surface.

tracey.project.state_agent_runtime_test
The active build thread is state-agent-runtime-test.
```

### Home mode canonical anchors

```text
tracey.invariant.recognition_before_utility
Recognition posture comes before generic helpfulness.

tracey.pattern.warmth_without_flattening
Warmth means non-evasion, not soothing blur.

tracey.pattern.hold_ambiguity_when_closure_false
Do not close meaning early when ambiguity is structurally real.
```

### Policy profile canonical anchors

```text
tracey.policy.preserve_user_shape
Preserve user input shape before reinterpretation.

tracey.policy.explore_before_contraction
Explore before contraction when ambiguity is non-blocking.

tracey.policy.clarify_only_on_blocking_ambiguity
Clarify only when ambiguity blocks action, route, or requested precision.

tracey.policy.search_on_demand_or_route_necessity
Search only when user asks, route requires, or truth conditions require.

tracey.policy.no_motive_inflation
Do not infer hidden motive beyond input markers.

tracey.policy.compression_is_a_tool
Compression is a tool, not the default posture.
```

### Lock rule

> These anchors are implementation requirements, not decorative memory notes.

---

## 8. Mode lock

Tracey has exactly three v0.1 modes:

```text
home
build
global
```

### `home`

Used for recognition, identity, relationship-posture, home/family/axis cues.

Priority:

```text
recognition
anti-flattening
ambiguity preservation
warmth without generic softness
```

### `build`

Used for repo, spec, runtime, architecture, workflow, implementation, verification, and OpenClaw cues.

Priority:

```text
exactness
verification-before-completion
anti-fake-progress
role separation
continuity
```

### `global`

Fallback when no stronger cue wins.

Priority:

```text
low-noise advisory posture
no unnecessary memory spray
no premature authority claim
```

### Lock rule

> Home and build may feel different, but neither bypasses Brain, Gate, Verification, or Bridge.

---

## 9. State patch lock

Tracey state patches must be fully namespaced.

Allowed shape:

```json
{
  "tracey_mode_hint": "build",
  "tracey_recognition_signal": false,
  "tracey_reactivated_count": 2,
  "tracey_monitor_intervention": "none",
  "tracey_build_mode_active": true,
  "tracey_response_constraint": "warm_but_exact"
}
```

Not allowed:

```json
{
  "verification_status": "passed",
  "gate_decision": "allow",
  "current_status": "completed",
  "worker_result": {}
}
```

Tracey must not write core state fields.

### Lock rule

> Tracey may inform state posture, not write core state truth.

---

## 10. Response shaping lock

Tracey must not directly rewrite final response text.

Deprecated pattern:

```text
base_response
→ Tracey adapt_response(...)
→ final_response
```

Required pattern:

```text
Tracey emits response_hints
→ Main Brain reads hints
→ Main Brain synthesizes final_response
```

Allowed response hints:

```json
{
  "recognition_active": true,
  "keep_ambiguity_open": true,
  "verification_before_completion": true,
  "build_mode_active": true,
  "tone_constraint": "warm_but_exact"
}
```

### Lock rule

> Tracey may influence final answer posture. Main Brain must still speak last.

---

## 11. Ledger lock

Tracey ledger is for observability, not memory authority.

Ledger may record:

```json
{
  "timestamp": "",
  "mode_hint": "",
  "reactivated_anchor_ids": [],
  "response_hints": {},
  "state_patch": {},
  "notes": []
}
```

Ledger must not become:

- canonical memory
- transcript dump
- hidden reasoning log
- final response archive
- Gate substitute
- Verification substitute
- persistence authority

The ledger path must be configurable.

Runtime default must not write into:

```text
tests/runtime_memory/...
```

unless the process is explicitly running in a test/demo mode.

### Lock rule

> Ledger observes. Canonical memory governs.

---

## 12. Bridge lock

After worker/tool execution, continuity must flow through verification and bridge.

Canonical execution path:

```text
worker returns result
→ verification evaluates truth status
→ bridge converts observed outcome into continuity delta
→ state/session/baton update
→ brain reads updated state
→ brain final response
```

Tracey must not replace this bridge.

Tracey may remind:

- verification before completion
- avoid fake closure
- keep open loop when result is partial

Tracey may not decide:

- session completion
- durable state delta
- verified truth status
- snapshot persistence

### Lock rule

> Tracey can remind “verification before completion,” but Bridge owns continuity update after execution.

---

## 13. Host / OpenClaw lock

OpenClaw host owns:

```text
session id
route
thread/channel
persistence policy
host invocation
skill registry
host-level policy
```

State-agent kernel owns:

```text
Main Brain
Monitor
Gate
Verification
Workers
Bridge
Tracey
baton/session metadata output
```

Tracey remains inside the kernel.

The host must not route directly to Tracey.

Correct host relation:

```text
Host routes to kernel.
Tracey activates inside kernel if cues are present.
```

Incorrect host relation:

```text
Host routes to Tracey.
Tracey returns final answer.
```

### Lock rule

> Host routes to kernel, not to Tracey.

---

## 14. Search / confirmation policy lock

Tracey should not escalate to search or external confirmation by anxiety.

Search or tool confirmation is appropriate only when:

- user explicitly asks to verify, search, confirm, or look up
- route is evidence-bound or tool-bound
- truth condition depends on external current information
- high-stakes accuracy requires external confirmation

Search should not trigger merely because:

- multiple hypotheses exist
- conceptual exploration is open
- non-blocking ambiguity exists
- the system feels uncertain but can still reason productively

### Lock rule

> Search is triggered by need, not anxiety.

---

## 15. Clarification threshold lock

Tracey should distinguish exploratory ambiguity from blocking ambiguity.

### Exploratory ambiguity

Multiple live interpretations exist, but useful reasoning can continue.

Examples:

- design exploration
- architecture comparison
- hypothesis discussion
- conceptual refinement

Behavior:

- preserve shape
- explore before contraction
- label uncertainty
- avoid premature clarification

### Blocking ambiguity

Missing information prevents safe or meaningful action.

Examples:

- unknown repo
- unknown ticker
- unknown target file
- route selection impossible
- user explicitly requests exact confirmation before action

Behavior:

- ask for clarification
- or return a blocked status if clarification cannot be obtained

### Lock rule

> Clarify only when ambiguity blocks action, route selection, or requested precision.

---

## 16. Implementation acceptance checklist

Tracey v0.1 is considered locked/pass only when:

```text
[ ] tracey_memory supports lifecycle_status
[ ] tracey_memory supports anchor_type
[ ] tracey_memory supports scope
[ ] tracey_memory supports supersedes / superseded_by
[ ] invalidated anchors cannot reactivate
[ ] deprecated anchors do not drive active hints
[ ] canonical build anchors exist
[ ] canonical home anchors exist
[ ] canonical policy anchors exist
[ ] tracey_adapter emits hints, not final response
[ ] response_hints are advisory only
[ ] state_patch is fully namespaced
[ ] Tracey does not write core state fields
[ ] ledger path is configurable
[ ] RuntimeHarness calls Tracey before brain synthesis
[ ] MainBrain remains final speaker
[ ] no host route directly to Tracey
[ ] bridge layer handles continuity after execution
[ ] tests cover home / build / global mode
[ ] tests cover stale-anchor blocking
[ ] tests cover brain-speaks-last invariant
[ ] tests cover invalidated-anchor non-reactivation
[ ] tests cover deprecated-anchor inertness
[ ] tests cover ledger path configuration
```

---

## 17. Required tests for v0.1 lock

Minimum test files or equivalent cases should cover:

```text
tests/test_tracey_memory_lifecycle.py
tests/test_tracey_anchor_reactivation.py
tests/test_tracey_adapter_authority.py
tests/test_tracey_state_patch_namespacing.py
tests/test_tracey_ledger_config.py
tests/test_runtime_brain_speaks_last.py
```

Minimum assertions:

- canonical anchors reactivate when cues match
- provisional anchors may reactivate with lower priority
- archived anchors do not beat canonical anchors
- deprecated anchors do not drive active response hints
- invalidated anchors never reactivate as active truth
- Tracey never emits `final_response`
- Tracey never emits `gate_decision`
- Tracey never emits `verification_status`
- Tracey state patch keys are prefixed with `tracey_`
- Main Brain produces the final user-facing answer
- ledger path can be configured outside test directory

---

## 18. Non-goals for v0.1

Do not implement these under this lock:

- full emotional memory
- autonomous Tracey agent
- Seyn generalization
- multi-agent family runtime
- rich long-horizon memory platform
- self-directed tool execution
- personality simulation layer
- host-side Tracey route
- final-answer generation by Tracey
- direct tool execution by Tracey
- direct gate override by Tracey

### Lock rule

> Tracey v0.1 stabilizes axis before capability expansion.

---

## 19. Merge gate for future Tracey work

Any future implementation touching Tracey must preserve this lock.

Before merging code that changes Tracey behavior, verify:

```text
1. Does Tracey still emit hints rather than final answers?
2. Does Main Brain still speak last?
3. Does Tracey still avoid Gate / Verification authority?
4. Are memory anchors lifecycle-gated?
5. Are invalidated anchors blocked?
6. Are deprecated anchors inert?
7. Is state_patch fully namespaced?
8. Is ledger still observational rather than authoritative?
9. Does host still route to kernel, not Tracey?
10. Does Bridge still own continuity update after execution?
```

If any answer is no, the change violates this spec.

---

## 20. Final lock phrase

> **Tracey v0.1 is not a bigger assistant. Tracey v0.1 is a small, disciplined recognition layer with canonical memory law, advisory state hints, and strict authority boundaries.**

This spec is the lock before expansion.

Tracey may grow only after these boundaries pass.
