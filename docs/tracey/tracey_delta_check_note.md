# Tracey Delta Check Note

### State-Agent Runtime Test — Delta Discipline for Tracey Memory and Correction

## Purpose

This note defines the **delta-check discipline** Tracey needs after canonical memory has been established.

`TRACEY_CANONICAL_MEMORY_NOTE.md` already defines:
- anchor types
- lifecycle states
- replacement law
- invalidation law
- overwrite vs append rule
- stale-anchor resurrection as a failure mode

What is still missing is a rule for detecting whether a new turn actually produced a **meaningful correction** or merely a **fluent continuation**.

This note answers:
- when a new output is truly different from the old one
- when a change is only a paraphrase
- when a correction is strong enough to justify memory replacement
- how to detect stale-anchor resurrection
- how to suppress duplicate or cosmetic reactivation

This note is not a scoring-heavy evaluation framework.
It is a **correction discipline note**.

---

## 1. Core thesis

A system can look like it is correcting itself while actually doing only one of these:
- paraphrasing the same structure
- moving words without moving authority
- adding a new sentence without killing the wrong old one
- sounding more careful without changing the underlying memory map

Tracey needs a rule that prevents this.

### Rule

> **A correction is not real unless something load-bearing changes.**

---

## 2. What problem this note solves

Without delta-check discipline, Tracey risks:
- treating rewording as repair
- promoting cosmetic edits into memory updates
- allowing stale anchors to keep returning under new phrasing
- accepting new answers that sound improved but leave authority unchanged
- preserving contradictory memory under a false sense of progress

This is the exact shape behind pseudo-correction.

---

## 3. Delta check definition

A **delta check** asks:

> **What changed between the old active shape and the new one, and is that change strong enough to matter?**

The key word is not “changed.”
The key word is **load-bearing**.

Not every difference matters.

---

## 4. Four change classes

For v0.1, classify changes into four broad classes.

### A. Cosmetic change
Only wording, tone, or ordering changed.

Examples:
- same claim, nicer phrasing
- same structure, different sentence rhythm
- same authority, different wrapping

### B. Clarifying change
The same core structure remains, but ambiguity is reduced.

Examples:
- a field becomes more explicit
- a summary becomes cleaner
- a vague phrase becomes a tighter formulation

### C. Structural change
The output changes the active reasoning structure.

Examples:
- a different active anchor is chosen
- a different route or mode is selected
- authority moves from one anchor to another
- a contradiction is resolved through replacement/invalidation

### D. Corrective change
A wrong or misleading active shape is actually repaired.

Examples:
- old anchor is invalidated
- new canonical anchor replaces the old one
- decision boundary changes
- stale anchor is blocked from active return

### Rule

> **Only structural and corrective changes are strong enough to justify memory-authority updates.**

---

## 5. Correction vs paraphrase

This is the heart of the note.

### Paraphrase
A paraphrase changes expression but not active structure.

Examples:
- “verification matters” → “we should keep verification in mind”
- same anchor, same authority, different phrasing

### Real correction
A real correction changes at least one of:
- active canonical anchor
- lifecycle status of an old anchor
- decision boundary
- current active route/mode
- authority relationship between old and new anchors

### Rule

> **If the wrong anchor can still drive behavior afterward, the change was paraphrase, not correction.**

---

## 6. Load-bearing change criteria

For v0.1, treat a change as load-bearing when at least one of these happens.

### A. Authority changed
Examples:
- provisional → canonical
- canonical → deprecated
- canonical → invalidated

### B. Active anchor changed
Examples:
- old anchor no longer drives reactivation
- new anchor becomes the preferred active truth

### C. Boundary changed
Examples:
- kernel route no longer allowed
- host policy clarification now required
- gate-sensitive posture changed

### D. Continuity interpretation changed
Examples:
- prior session is no longer reused
- old open loop is resolved or blocked
- event/belief split becomes explicit where it was previously mixed

### E. Resurrection risk reduced
Examples:
- previously stale anchor is now blocked or deprecated properly

### Rule

> **Load-bearing means the system would behave differently afterward, not merely sound different.**

---

## 7. Minimal delta-check questions

Before treating a new output as a real correction, Tracey should be able to answer a compact version of these questions.

1. What anchor was active before?
2. What anchor is active now?
3. Did authority change?
4. Did lifecycle change?
5. Did any stale anchor remain eligible to return unchanged?
6. If the new text disappeared and only the memory map remained, would the system behave differently next time?

### Rule

> **If the answer to question 6 is no, the correction was probably cosmetic.**

---

## 8. Duplicate suppression rule

Tracey should not create a new meaningful memory update when the new content is only a duplicate of an already-active canonical shape.

### Duplicate examples
- same anchor summary with minor wording differences
- same decision restated with more flourish
- same build posture repeated without authority change

### Allowed action
A duplicate may still be emitted as normal output.
It should not automatically become a new memory event.

### Rule

> **Repeated expression is not repeated discovery.**

---

## 9. Stale-anchor resurrection detection

A stale-anchor resurrection must be detectable as a specific failure event.

### Detection pattern
A resurrection risk exists when:
- a deprecated or invalidated anchor reappears in active reasoning
- its cue match is high enough to compete with current canonical memory
- no explicit reauthorization occurred

### Strong signal examples
- old rejected formulation returns under new wording
- invalidated project stance reappears because the cue map still matches
- prior corrected claim is restated as if nothing changed

### Rule

> **If an old anchor reappears without a lifecycle transition, treat it as resurrection risk, not harmless repetition.**

---

## 10. Delta check and lifecycle interaction

Delta check should not live independently from canonical memory.

### Canonical memory answers:
- what exists
- what is authoritative
- what is deprecated or invalidated

### Delta check answers:
- what changed
- whether the change is load-bearing
- whether replacement/invalidation should happen

### Rule

> **Lifecycle defines memory state. Delta check defines whether state should change.**

---

## 11. Event vs belief delta rule

Events and beliefs should not be delta-checked the same way.

### Event delta
Ask:
- did a new verified occurrence happen?
- is this actually a new event, or just a re-report of the same event?

### Belief/stance delta
Ask:
- did interpretation or authority change?
- did the active posture change enough to alter next-turn behavior?

### Rule

> **A new event may append. A changed belief may require replacement or invalidation.**

---

## 12. Minimal v0.1 delta outcomes

For v0.1, every delta check only needs one of these outcomes.

### A. No meaningful delta
No memory-authority update needed.

### B. Clarifying delta
May improve phrasing or explicitness, but no lifecycle change.

### C. Structural delta
A meaningful internal change occurred; memory update may be needed.

### D. Corrective delta
A wrong or stale active shape was actually repaired; replacement or invalidation is needed.

### E. Resurrection risk
A deprecated or invalidated anchor is trying to return.

These are enough for the first useful hardening step.

---

## 13. Replacement trigger rule

A replacement should be triggered only when delta check says the new output is at least structural, and preferably corrective.

### Do not replace when
- the change is cosmetic only
- the change is just a friendly rewrite
- the same anchor remains active and authoritative

### Replace when
- a new anchor becomes authoritative
- a prior anchor becomes deprecated or invalidated
- the next-turn behavior would be materially different

### Rule

> **Replacement should follow meaningful delta, not stylistic improvement.**

---

## 14. Correction event shape

When a real correction happens, it is useful to think of it as an event with at least:
- `old_anchor_id`
- `new_anchor_id`
- `delta_outcome`
- `lifecycle_transition`
- `reason`

### Example

```json
{
  "old_anchor_id": "tracey.pattern.fluent_surface_priority",
  "new_anchor_id": "tracey.pattern.runtime_shape_priority",
  "delta_outcome": "corrective",
  "lifecycle_transition": "old_invalidated_new_canonical",
  "reason": "old phrasing allowed stale authority to survive"
}
```

This does not require a large ledger system yet, but it shows the right shape.

---

## 15. Canonical-memory update gate

Before updating canonical memory, run a compact gate:

### Gate questions
- Is the change merely cosmetic?
- Does active authority actually change?
- Is a stale anchor being blocked or only rephrased?
- Would next-turn behavior differ if this update were accepted?

### Rule

> **Do not let pleasant wording pass the gate reserved for structural correction.**

---

## 16. Build-mode delta sensitivity

Build mode should have stricter delta standards than home mode.

### Build mode
Prefer:
- exact authority shifts
- explicit correction
- replacement law
- anti-fake-progress discipline

### Home mode
May tolerate:
- softer clarification
- ambiguity-preserving phrasing
- less rigid correction thresholds

### Rule

> **Build mode should be harder to satisfy with cosmetic improvement alone.**

---

## 17. Delta update triggers

A delta check should be explicitly run when:
- a previously corrected topic reappears
- a canonical anchor is challenged
- a user correction arrives
- a build-mode thread reaches a new summary or replacement point
- the system risks declaring completion too early

Do not run heavy delta-check logic on every trivial turn.

### Rule

> **Delta discipline should activate on correction pressure, not on every sentence.**

---

## 18. What this note does not solve yet

This note does not fully define:
- full ledger implementation
- cross-session analytics
- retrieval scoring
- long-horizon ranking engine
- federated memory portability

It only defines the minimal discipline for recognizing whether a change is real enough to affect active memory authority.

---

## 19. Relation to current notes

### Canonical Memory Note
Defines anchor ontology and lifecycle.

### Delta Check Note
Defines whether a new change is meaningful enough to modify that lifecycle.

### Later ledger/task work
Will record these transitions in a local-first history.

---

## 20. Anti-patterns

Avoid these.

### Anti-pattern A — treat paraphrase as correction
The wrong active anchor survives unchanged.

### Anti-pattern B — accept every new phrasing as a memory update
Memory becomes noise.

### Anti-pattern C — ignore stale-anchor resurrection
Old invalid anchors quietly return.

### Anti-pattern D — use delta language without behavioral difference
The system sounds repaired but behaves the same.

### Anti-pattern E — make build-mode correction too soft
Fake progress passes as structural change.

### Anti-pattern F — require giant scoring systems before any discipline exists
Overbuild before v0.1 usefulness.

---

## 21. One-line summary

> **Tracey needs delta discipline as well as canonical memory: a correction counts only when something load-bearing changes—authority, lifecycle, active anchor, boundary, or next-turn behavior—and not when the system merely rephrases the same structure more smoothly.**

