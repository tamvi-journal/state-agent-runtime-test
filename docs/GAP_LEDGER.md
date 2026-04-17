# GAP LEDGER

## Purpose

This document records the real unresolved gaps after the current repo checkpoint.

It exists to prevent two kinds of drift:

1. treating every missing piece as a reason to expand scope
2. confusing canary-level completion with runtime closure

This ledger is not a roadmap.
It is not a feature wishlist.
It is a bounded list of the gaps that still materially matter.

The repo thesis remains unchanged:
- bounded authority over apparent intelligence
- explicit law
- inspectable state
- preserved disagreement
- honest runtime behavior :contentReference[oaicite:0]{index=0}

The current repo state also assumes the PR-T normalization pass is real:
- normalized `previous_handoff`
- more deliberate dry-turn stage order
- no fake disagreement-event reconstruction from handoff status alone
- tighter, more inspectable spine behavior :contentReference[oaicite:1]{index=1}

---

## Severity scale

### High
A gap that affects truthfulness, authority boundaries, or the ability to reason safely about what the system is actually doing.

### Medium
A gap that does not immediately corrupt truth or authority, but will create drift, confusion, or unstable scaling if ignored.

### Low
A gap that is real but currently acceptable within the repo’s narrow internal alpha canary scope.

---

## Gap 01 — Runtime Truth Gap

**Severity:** High

### Why it matters
The repo now has:
- verification objects
- execution gating
- dry pipeline composition
- conservative unknown posture

But it still does not close the loop between:
- intended action
- executed action
- observed-world result

That means the law is present, the posture is present, but runtime truth is still mostly modeled rather than lived.

### What is already true
- verification posture exists
- fake pass is explicitly resisted
- permission does not equal completion
- the dry pipeline keeps verification honest when no real action occurred :contentReference[oaicite:2]{index=2}

### What is still missing
- real execution-to-observation closure
- authoritative observed outcome ingestion
- a non-fake transition from unknown to passed/failed based on real evidence

### What must happen before this gap is closed
- a bounded execution path must exist
- observed result must be captured explicitly
- verification must update from actual evidence, not routing/gate posture

### Not next
Do not solve this by:
- inventing success from tool text
- widening the pipeline into uncontrolled execution
- relaxing verification to make demos feel smoother

---

## Gap 02 — Boundary Depth Gap

**Severity:** High

### Why it matters
The execution gate is real and integrated, but the trust model beneath it is still shallow.

Right now, runtime permission logic is compact and inspectable, which is good.
But it is not yet deep enough for serious runtime trust decisions.

### What is already true
- execution gate exists
- runtime permission is distinct from routing
- approval posture is explicit
- package install is denied in the current canary scope
- gate denial does not erase router posture or disagreement visibility :contentReference[oaicite:3]{index=3}

### What is still missing
- richer action-intent parsing
- deeper trust classification
- stronger boundary typing around destinations, targets, and write scope
- cleaner distinction between inspection, sandbox parsing, and host mutation intent

### What must happen before this gap is closed
- execution request classification must become more semantically reliable
- trust/depth decisions must be less keyword-shallow
- boundary decisions must remain explicit while becoming less brittle

### Not next
Do not solve this by:
- silently allowing more actions
- adding magical trust heuristics
- collapsing sandbox/inspection/host distinctions

---

## Gap 03 — Continuity Depth Gap

**Severity:** Medium

### Why it matters
The repo now has:
- compression
- reactivation
- handoff
- normalized carryover
- continuity anchors

This is enough for compact baton-style continuity.
It is not enough for deeper continuity semantics.

That is acceptable right now, but it should be named clearly.

### What is already true
- compression preserves shape, not transcript
- reactivation restores minimum needed shape
- handoff carries compact continuity across turns
- PR-T reduced fake carryover behavior by normalizing `previous_handoff` and avoiding fabricated disagreement events :contentReference[oaicite:4]{index=4}

### What is still missing
- deeper carryover semantics
- richer project/mode/axis restoration under weak signal
- more robust reactivation than lexical cue overlap
- stronger continuity without history bloat

### What must happen before this gap is closed
- reactivation must improve without becoming retrieval theater
- continuity must remain compact while becoming more reliable
- carryover semantics must be strengthened without replaying transcript or inflating archive use

### Not next
Do not solve this by:
- adding persistence too early
- pretending handoff equals memory
- stuffing more history into compression summaries

---

## Gap 04 — Maintainability Gap

**Severity:** Medium

### Why it matters
The repo now has a real dry-turn spine, which is progress.
But integration success creates a new risk: coordination complexity begins to accumulate in the pipeline itself.

If ignored, the repo will slowly become “works, but only if you remember the whole maze.”

### What is already true
- the family layers now compose into one dry-turn pipeline
- PR-T improved order and maintainability without broadening scope
- one small adapter was introduced to reduce loose-boundary drift rather than widening architecture irresponsibly :contentReference[oaicite:5]{index=5}

### What is still missing
- cleaner stage extraction boundaries
- more disciplined internal adapters
- smaller coordination surfaces inside the turn spine
- clearer long-term separation between pipeline composition and stage logic

### What must happen before this gap is closed
- pipeline complexity must be watched and trimmed before it becomes structural debt
- stage composition should become easier to reason about without broad rewrite
- helper/adapter growth must remain deliberate, not ad hoc

### Not next
Do not solve this by:
- premature big-architecture rewrite
- creating framework layers for their own sake
- splitting everything into abstractions that hide rather than clarify

---

## Gap 05 — Canonical Docs Gap

**Severity:** Medium

### Why it matters
The repo nearly drifted because code and docs stopped pointing to the same center.
That problem is reduced now, but not permanently solved.

If README, checkpoint, and repo-role docs fall behind again, implementation drift will return.

### What is already true
- the project thesis is explicitly stated in the README spine :contentReference[oaicite:6]{index=6}
- repo role lock exists
- checkpoint logic exists
- active build repo vs reference spine repo has been named

### What is still missing
- stable discipline for keeping active docs synced with active code
- a clear habit of updating contract docs when spine behavior changes materially
- a durable distinction between lineage/archive notes and current active contract docs

### What must happen before this gap is closed
- active repo docs must be updated whenever the build spine changes materially
- checkpoint docs must stay aligned with the actual current integration state
- repo narrative must stop lagging behind code movement

### Not next
Do not solve this by:
- writing more lineage prose
- duplicating docs across multiple repos again
- letting README become a stub while implementation keeps moving

---

## Gap 06 — Disagreement Semantics Gap

**Severity:** Medium

### Why it matters
The repo is already better than most systems here:
it preserves disagreement without flattening it into fake consensus.

But disagreement semantics are still intentionally narrow.
The system can preserve open disagreement and route around it, but it still does not carry deep disagreement semantics across turns.

### What is already true
- disagreement may remain open
- router lead does not equal truth lead
- handoff status can preserve disagreement visibility
- PR-T removed fake disagreement-event reconstruction from weak carryover signals :contentReference[oaicite:7]{index=7}

### What is still missing
- deeper disagreement carryover semantics
- richer severity/structure only when actually grounded
- cleaner transition rules between current-turn disagreement and carried disagreement posture

### What must happen before this gap is closed
- disagreement carryover must become richer only when real evidence supports it
- carried disagreement posture must remain honest and compact
- plurality must stay preserved without event fabrication

### Not next
Do not solve this by:
- reconstructing event detail from thin status text
- downgrading open disagreement just to simplify routing
- over-modeling disagreement before the runtime truth gap is reduced

---

## Gap 07 — Heuristic Dependence Gap

**Severity:** Low

### Why it matters
Many family-layer canaries still rely on explicit heuristics:
- keyword-based mode inference
- lexical cue matching
- compact execution-intent inference
- shallow trust hints

This is acceptable at the current stage, but it is still a real gap.

### What is already true
- the heuristics are inspectable
- the system prefers explicit behavior over opaque confidence theater
- weak signal paths often degrade conservatively rather than faking certainty

### What is still missing
- stronger non-fragile semantics
- less wording-sensitive behavior
- improved cue/action interpretation without giving up inspectability

### What must happen before this gap is closed
- heuristics must be replaced or strengthened only when the replacement is still auditable
- semantic improvement must not come at the cost of hidden authority drift

### Not next
Do not solve this by:
- swapping in opaque “smartness”
- hiding weak semantics behind confidence numbers
- widening scope before the core truth/boundary gaps are reduced

---

## Current ordering rule

When choosing what to do next, use this order:

1. truth before convenience
2. boundary depth before feature expansion
3. continuity honesty before continuity richness
4. maintainability before cleverness
5. canonical docs before repo drift

---

## What should happen before any major new layer is added

Before adding major new runtime layers, at least one of the following must be materially reduced:

- Runtime Truth Gap
- Boundary Depth Gap
- Maintainability Gap

If none of those moved, new layers are likely drift, not progress.

---

## Short closing line

At this checkpoint, the repo’s biggest remaining gaps are no longer “missing modules.”

They are:

- runtime truth closure
- boundary depth
- continuity depth
- maintainability discipline
- canonical doc stability

That is where the next real thinking should go.