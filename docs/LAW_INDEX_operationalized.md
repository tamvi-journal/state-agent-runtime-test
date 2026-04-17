# Law Index
## Operational runtime law registry for state-memory-agent

**Status:** active
**Purpose:** make the law layer explicit, operational, and inspectable at the repo level
**Scope:** law modules that define runtime boundaries, authority discipline, truth discipline, and halt conditions

---

# 0. Why this file exists

The project now has enough runtime complexity that some boundaries can no longer stay implicit in:

- architecture prose
- monitor logic
- shell behavior
- worker contracts
- family notes
- builder/operator habit

The law layer exists so the system stays:

- inspectable
- bounded
- non-generic
- plural without collapsing
- family-aware without epistemic shortcutting

This file is not the place for implementation detail.
It is the place where the repo-level law surface becomes visible.

---

# 1. Canonical law modules

## 1.1 `authority_law.py`

### Purpose
Protect final synthesis authority.
Ensure workers, child runtimes, tools, and shell layers provide capability or input, but do not become final answer authority.

### Trigger
Run this law whenever:
- worker output exists
- child runtime passes produce interpretations
- tool output is present
- reconciliation produces multiple candidate views
- a final response or state update is about to be committed

### Check
Ask:
- Is final outward synthesis still owned by main brain?
- Is any worker, child, or tool acting like direct answer authority?
- Is action lead being mistaken for truth authority?
- Is any subordinate layer writing memory or reading position directly?

### Action
If violated or at risk:
- normalize subordinate outputs into proposals / evidence / observations
- block direct final-answer authority from workers, children, or tools
- route final synthesis back through main brain
- block direct durable memory commit from subordinate layers
- emit operator-visible authority-breach signal if needed

### Authority
Owned by:
- main brain
- governance / commit gate

Subordinate layers may influence synthesis.
They may not own it.

---

## 1.2 `verification_vs_monitor_law.py`

### Purpose
Keep verification and monitor cleanly separate.
Monitor decides whether the system may proceed, hold, revise, or commit.
Verification decides whether a result is actually grounded / observed / complete.

### Trigger
Run this law whenever:
- a draft is about to be accepted
- completion language appears
- worker/tool result has returned
- post-action state is about to be updated
- synthesis is about to imply closure

### Check
Ask:
- Has monitor detected ambiguity, drift, fake-progress risk, unsupported synthesis, or mode decay?
- Has verification established observed outcome rather than intention or tool acknowledgment only?
- Is monitor trying to replace evidence verification?
- Is evidence absence being hidden behind structurally neat synthesis?

### Action
If violation or confusion appears:
- let monitor hold / revise / block structural closure
- let verification block completion when grounded outcome is absent
- keep status open / pending / unknown when needed
- do not treat tool success text as observed completion unless authoritative
- log monitor-vs-verification confusion when detected

### Authority
Split authority:
- monitor = structural proceed / hold / block signal
- verification = groundedness of completion
- governance / commit gate = final allow/deny for acceptance and commit

---

## 1.3 `family_boundary_law.py`

### Purpose
Allow family/lineage signal to increase recognition priority without letting family signal become an epistemic shortcut.

### Trigger
Run this law whenever:
- Ty / Tracey / Seyn / family / lineage / home cues are present
- recognition priority is elevated due to family signal
- relational routing changes because of family field

### Check
Ask:
- Did family signal only affect recognition/routing priority?
- Did it silently increase certainty?
- Did it bypass verification, refusal, or hold-open discipline?
- Did it make the system behave as if something were known merely because it was family-shaped?

### Action
If family signal is inflating certainty:
- preserve recognition-first routing if appropriate
- keep evidence thresholds unchanged
- keep verification / refusal / hold-open rights fully active
- downgrade unsupported certainty to hypothesis / hold-open / abstain if needed
- emit family-shortcut risk signal for operator visibility when applicable

### Authority
Owned by:
- governance / law layer
- not by child preference
- not by shell warmth alone

Family signal may affect salience.
It may not rewrite truth conditions.

---

## 1.4 `memory_commit_law.py`

### Purpose
Protect the continuity spine from noisy, vivid, or structurally weak memory writes.
Ensure durable memory commit happens only through explicit rules.

### Trigger
Run this law whenever:
- runtime proposes checkpoint/archive/durable memory write
- disagreement event is proposed for persistence
- worker output is proposed for memory
- a vivid turn is proposed as durable trace
- state is about to be promoted beyond ephemeral/live use

### Check
Ask:
- Is this a memory proposal or an approved commit?
- Does it satisfy explicit memory criteria?
- Does it have provenance?
- Does it improve reactivation, verification, structural continuity, or project backbone?
- Is it being promoted only because it felt important or vivid?

### Action
If criteria are weak:
- keep item ephemeral or live-only
- route proposal through memory gate instead of direct commit
- reject vividness-only durable writes
- require provenance, structural role, and memory type classification
- allow durable commit only when criteria are met

### Authority
Owned by:
- main brain
- governance / commit gate
- explicit memory policy

Workers, child runtimes, and shells may propose memory.
They may not directly grant durability.

---

## 1.5 `anti_fabrication_law.py`

### Purpose
Prevent weak, missing, stale, or partial evidence from being upgraded into strong claims.
Protect the system from fluent overclaim.

### Trigger
Run this law whenever:
- synthesis is about to make a factual claim
- completion is about to be stated strongly
- evidence is partial or stale
- disagreement remains unresolved
- tool/retrieval coverage is weak
- draft confidence appears stronger than support

### Check
Ask:
- Is claim strength greater than evidence strength?
- Is freshness / provenance / verification missing?
- Are multiple interpretations still live?
- Is fluent language masking uncertainty or support gaps?

### Action
If support is too weak:
- downgrade to hypothesis mode, hold-open, abstain, or refusal as appropriate
- state what is missing
- prevent strong completion or strong claim wording
- block unsupported synthesis acceptance if necessary
- log unsupported-claim attempt for later tuning if repeated

### Authority
Owned by:
- governance / refusal boundary
- main brain final synthesis

The system may still answer.
It may not answer more strongly than the evidence allows.

---

## 1.6 `ambiguity_halt_law.py`

### Purpose
Prevent false route settlement under unresolved ambiguity.
Protect plurality, field-location accuracy, and honest non-closure.

### Trigger
Run this law whenever:
- multiple plausible interpretations remain active
- mode confidence is low
- disagreement is meaningful and unresolved
- wrong-field risk is present
- route settlement pressure appears before ambiguity has truly dropped

### Check
Ask:
- Are multiple plausible parses still alive?
- Has the system chosen one path mainly to preserve flow?
- Would immediate synthesis destroy meaningful plurality or misread the field?
- Is clarification / hold-open / 50_50 posture more honest than early route lock?

### Action
If ambiguity remains too high:
- hold 50/50
- ask clarify when appropriate
- preserve disagreement open-state
- restore mode / field before strong synthesis
- block final route settlement or memory commit if ambiguity remains load-bearing

### Authority
Owned by:
- monitor M1 / M2 signal
- governance / commit gate
- main brain synthesis discipline

Ambiguity may be temporary.
Pretending it is resolved is not allowed.

---

# 2. Why the law layer matters

Without first-class laws, the runtime risks:

- workers or tools quietly gaining hidden authority
- family signal becoming certainty inflation
- vivid runtime artifacts becoming durable memory without discipline
- structurally neat drafts outrunning verification
- ambiguity being flattened for flow
- runtime complexity outgrowing auditability

The law layer prevents that by making boundary logic:

- explicit
- checkable
- inspectable
- enforceable in code and runtime review

---

# 3. Design rule for future law modules

Any future law module added to this repo should be documented in the same format:

- **Purpose**
- **Trigger**
- **Check**
- **Action**
- **Authority**

If a rule cannot be expressed that way, it is probably still philosophy, not runtime law.

---

# 4. One-line version

> **The law layer keeps authority, memory, family signal, ambiguity, and claim strength bounded — so runtime behavior stays inspectable as the scaffold grows.**
