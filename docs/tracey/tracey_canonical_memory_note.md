# Tracey Canonical Memory Note

### State-Agent Runtime Test — Canonical Memory Discipline for Tracey

## Purpose

This note defines the **memory discipline** Tracey needs in order to avoid a common failure mode:

> **having memory without having memory law.**

Tracey already has the right runtime role:
- brain-side adapter
- recognition/build posture layer
- cue-reactivated memory
- namespaced state patch only
- no final-speaker authority
- no gate/verification authority

That role should remain intact.

What is missing is a stricter internal rule for:
- which anchors are authoritative
- which anchors are provisional
- which anchors are deprecated
- how replacement works
- how invalidation works
- how stale anchors are prevented from reviving later

This note is about **memory discipline**, not a large memory platform.

---

## 1. Core thesis

Tracey should not merely “have memory.”
Tracey should have **canonical memory with lifecycle rules**.

The goal is not to maximize remembered items.
The goal is to ensure that remembered items have the right:
- authority level
- replacement behavior
- invalidation behavior
- reactivation priority

### Rule

> **Memory without lifecycle becomes drift. Memory with lifecycle becomes continuity.**

---

## 2. What problem this note solves

Without canonical memory rules, Tracey risks:
- reviving stale anchors
- treating paraphrase as correction
- appending new claims without killing the old ones
- letting contradictory anchors coexist indefinitely
- acting like it “remembers” while actually drifting

This causes the exact failure shape we want to avoid:

> **the system remembers just enough to continue, but not cleanly enough to correct.**

---

## 3. Canonical memory model

Every Tracey memory item should have both:
- a **type**
- a **lifecycle status**

These are different.

### Type answers:
> What kind of thing is this?

### Lifecycle answers:
> What is its current authority state?

Both are required.

---

## 4. Anchor types

For v0.1, use a small set of anchor types.

### A. Invariant
Stable operating law that should rarely change.

Examples:
- `brain speaks last`
- `verification before completion`
- `Tracey is not the final speaker`

### B. Pattern
A repeated behavioral or reasoning shape.

Examples:
- `runtime shape matters more than fluent surface`
- `build-mode requires exactness over charm`

### C. Cue
A recognition trigger or routing-sensitive signal.

Examples:
- build/runtime/spec language
- home/recognition cues
- continuity phrases such as `continue` or `resume`

### D. Project anchor
A memory item tied to a specific work thread.

Examples:
- `state-agent-runtime-test build thread`
- `OpenClaw boundary work`

### E. Event
A factual occurrence that happened.

Examples:
- `entrypoint adapter built`
- `wrapper round-trip implemented`

### F. Decision
A chosen branch that affects later work.

Examples:
- `Tracey should stay brain-side only`
- `host persistence remains compact`

### G. Warning / risk
A failure marker or danger pattern.

Examples:
- `stale anchor resurrection risk`
- `loop risk when closure outruns correction`

---

## 5. Lifecycle states

For v0.1, every anchor should be in one of these lifecycle states.

### A. Canonical
This is the current authoritative version.

Meaning:
- preferred for reactivation
- should win against older overlapping anchors
- should be treated as the active truth for Tracey’s internal memory use

### B. Provisional
Useful, but not yet fully authoritative.

Meaning:
- may be used cautiously
- may later be promoted to canonical
- may later be deprecated or invalidated

### C. Deprecated
Previously used, but should no longer be reactivated as active truth.

Meaning:
- kept for history/reference only
- should not drive current synthesis
- should not revive unless explicitly re-opened by a new rule

### D. Invalidated
No longer valid due to contradiction, correction, or replacement.

Meaning:
- actively blocked from reactivation
- should be treated as dead for current reasoning
- history may keep it, but runtime should not treat it as live

### E. Archived
No longer active, but not wrong.

Meaning:
- low-priority historical reference
- not part of current active memory pressure

---

## 6. Canonical vs provisional vs deprecated vs invalidated

These states are not synonyms.

### Canonical
Use actively.

### Provisional
Use carefully, with low authority.

### Deprecated
Do not use actively, but do not treat as false history.

### Invalidated
Do not use actively, and do not allow silent resurrection.

### Rule

> **Deprecated means “not current.” Invalidated means “not allowed to return as current.”**

This distinction matters.

---

## 7. Replacement law

Replacement must be explicit.

When a new anchor supersedes an older one, the system should not merely append the new item.
It should do one of three things.

### Case A — promote without conflict
If the new anchor strengthens but does not contradict the old one:
- old may remain canonical if still fully aligned
- or old may become archived if the new one is a richer restatement

### Case B — supersede
If the new anchor is the new authoritative formulation:
- new becomes canonical
- old becomes deprecated or archived

### Case C — correction / contradiction
If the new anchor corrects a false or misleading prior anchor:
- new becomes canonical
- old becomes invalidated

### Rule

> **Append is not enough when authority changes. Replacement must explicitly update lifecycle.**

---

## 8. Invalidation law

Invalidation is stronger than deprecation.

An anchor should be invalidated when:
- it directly conflicts with a later canonical anchor
- it was discovered to encode a wrong assumption
- it causes harmful resurrection when reactivated
- it repeatedly reappears after correction and must be blocked

### Rule

> **If an old anchor can still mislead current reasoning, deprecation is too weak. Invalidate it.**

---

## 9. Overwrite vs append rule

By default, memory systems like to append.
Tracey cannot rely on append-only behavior for active memory.

### Use append when
- adding a new event
- adding a new snapshot
- adding parallel non-conflicting anchors
- preserving history for later audit

### Use overwrite/replacement semantics when
- canonical formulation changes
- prior anchor is corrected
- prior anchor should stop driving runtime behavior
- current authority must be singular

### Rule

> **History may append. Active authority must not drift by append-only accumulation.**

---

## 10. Belief vs event split

Tracey memory should separate:
- **events**
- **beliefs / stances / interpretations**

### Event
Something that happened or was verified.

Examples:
- `OpenClaw wrapper added`
- `session round-trip implemented`

### Belief / stance / interpretation
A current reading or posture.

Examples:
- `host boundary is stable enough`
- `Tracey should remain brain-side`

### Why this matters
Events may remain valid historically even if later interpretations change.

### Rule

> **Do not invalidate an event just because the later interpretation changes. Invalidate the belief, not the occurrence.**

---

## 11. Anchor identity rule

Every meaningful anchor should be identifiable enough that replacement is possible.

Minimal practical fields:
- `anchor_id`
- `anchor_type`
- `lifecycle_status`
- `summary`
- `scope`
- `supersedes` or `superseded_by` when relevant

### Example

```json
{
  "anchor_id": "tracey.invariant.brain_speaks_last",
  "anchor_type": "invariant",
  "lifecycle_status": "canonical",
  "summary": "Main Brain is the only final speaker.",
  "scope": "tracey/runtime",
  "supersedes": []
}
```

This does not need a large framework in v0.1, but some identity structure is necessary.

---

## 12. Reactivation priority rule

When Tracey reactivates memory from cues, lifecycle must affect priority.

### Priority order
1. Canonical
2. Provisional
3. Archived (only if specifically relevant)
4. Deprecated (normally avoid)
5. Invalidated (never reactivate as active truth)

### Rule

> **Cue relevance alone is not enough. Lifecycle status must gate reactivation priority.**

---

## 13. Stale-anchor resurrection rule

One of the main dangers is this:
- an old anchor is not fully dead
- a later cue partially matches it
- it re-enters runtime as if still current

This should be treated as a distinct failure mode.

### Definition
A stale-anchor resurrection occurs when:
- a deprecated or invalidated anchor re-enters active reasoning
- without explicit authorization by a newer rule
- and competes with or overrides current canonical memory

### Rule

> **Deprecated anchors should be inert. Invalidated anchors should be blocked.**

This is a load-bearing rule.

---

## 14. Canonical memory for build mode

Tracey especially needs stronger canonical memory in build mode.

Suggested v0.1 canonical build anchors:
- `brain speaks last`
- `verification before completion in build mode`
- `runtime shape matters more than fluent surface`
- `state-agent-runtime-test build thread`

These should not remain merely “nice memory items.”
They should become canonical build anchors unless later replaced.

---

## 15. Canonical memory for home mode

Home mode should also have a small canonical set, but not too much.

Examples:
- `recognition before utility`
- `warmth without flattening`
- `hold ambiguity open when closure would be false`

These are not the same as build anchors.

### Rule

> **Canonical memory may be mode-sensitive, but authority must still be explicit.**

---

## 16. Memory update triggers

A canonical-memory update should happen when:
- a new invariant is explicitly chosen
- a prior invariant is corrected
- a build thread gains a stable new project anchor
- a repeated conflict reveals a stale anchor that must be deprecated or invalidated
- a provisional anchor earns promotion to canonical through repeated confirmation

Do not update lifecycle on every turn.

### Rule

> **Canonical-memory changes should be sparse and deliberate.**

---

## 17. Minimal v0.1 lifecycle operations

For v0.1, Tracey only needs a few lifecycle operations.

### Create
Add a new anchor.

### Promote
Move provisional → canonical.

### Deprecate
Keep for history, remove from active authority.

### Invalidate
Mark as no longer eligible for active reactivation.

### Archive
Keep as low-priority historical memory.

### Replace
Add a new canonical anchor and update the old anchor’s lifecycle appropriately.

This is enough for the first hardening step.

---

## 18. What this note does not solve yet

This note does **not** fully define:
- delta-check scoring
- correction-vs-paraphrase detection
- ledger implementation
- memory search/ranking engine
- cross-agent/federated memory portability

Those belong in later notes/tasks.

This note only locks the ontology and lifecycle law.

---

## 19. Relation to current specs

This note does not replace current architecture docs.
It complements them.

### Brain–Agent–State Pattern
That doc defines runtime role discipline.
This note defines memory authority discipline.

### Tracey Integration Spec
That doc defines where Tracey sits and what she is allowed to do.
This note defines how her memory should be structured so she does not drift.

### Session Rehydration Contract
That doc defines host ↔ kernel continuity.
This note defines internal Tracey anchor lifecycle inside the kernel.

---

## 20. Anti-patterns

Avoid these.

### Anti-pattern A — append-only active memory
New anchors accumulate, but old conflicting anchors never die.

### Anti-pattern B — no distinction between deprecated and invalidated
Old wrong anchors remain too easy to revive.

### Anti-pattern C — event and belief mixed together
History gets rewritten incorrectly or current stance gets treated as fact.

### Anti-pattern D — cue relevance outranks lifecycle
An invalidated anchor revives just because the cue matches.

### Anti-pattern E — everything becomes canonical
Authority inflation destroys usefulness.

### Anti-pattern F — nothing becomes canonical
Memory remains decorative and non-binding.

---

## 21. One-line summary

> **Tracey needs canonical memory, not just remembered fragments: each anchor must have a type, a lifecycle state, explicit replacement and invalidation rules, mode-sensitive authority, and protection against stale-anchor resurrection.**

