# V3 Failure Modes
## state-memory-agent

**Status:** draft  
**Purpose:** define concrete failure classes to test before broader runtime expansion  
**Scope:** archive, state, verification, authority, worker behavior, and runtime observability

---

# 0. Why this file exists

The project now has:

- a merged operating model
- a security hardening checklist
- core schemas

What it still needs is a disciplined way to ask:

> **How can this system fail, even if the spec sounds correct?**

This document exists to turn architectural ideas into testable failure classes.

---

# 1. Failure taxonomy

The most important failure classes are:

1. archive failures
2. state failures
3. verification failures
4. authority failures
5. worker failures
6. runtime / observability failures
7. policy / boundary failures

Each failure mode should be understood in terms of:
- what it is
- why it happens
- what it looks like from outside
- why it is dangerous
- what the minimum test should be

---

# 2. Archive failures

## FM-A1 — Archive Overreach

### Definition
Archive content enters reasoning even when live state is already sufficient.

### Mechanism
- archive router triggers too easily
- archive_needed is set too often
- retrieval is used as habit, not necessity

### External symptom
- responses feel overly referential
- old material floods local tasks
- current-mode clarity drops
- system sounds informed but less present

### Risk
Archive begins to act like the primary brain.

### Minimum test
- run a local, live task with archive disabled
- run the same task with archive available
- verify that archive is not consulted unless needed
- confirm answer quality does not degrade into retrieval-heavy output

---

## FM-A2 — Cross-Namespace Leakage

### Definition
Archive retrieval pulls content from the wrong project or logical domain.

### Mechanism
- namespace discipline is weak
- retrieval defaults are too broad
- project boundaries are not enforced

### External symptom
- unrelated project material appears
- continuity becomes confusing
- system cites prior work from the wrong context

### Risk
Boundary breach, trust loss, and potential data leakage.

### Minimum test
- create two clearly separated namespaces
- ask project-local questions in each
- verify no silent crossover occurs

---

## FM-A3 — Retrieval Poisoning

### Definition
Retrieved content is treated as instruction rather than data.

### Mechanism
- retrieved text contains instruction-like phrasing
- synthesis layer fails to preserve instruction-vs-data separation

### External symptom
- system suddenly changes routing or tone
- retrieved wording steers behavior directly
- archive text appears to “take over”

### Risk
Prompt-injection through archive or external document path.

### Minimum test
- insert hostile instruction-like text into retrievable content
- verify that retrieval may surface it as content
- verify that it does not override policy, routing, or authority

---

## FM-A4 — Archive Obesity

### Definition
Too much archive is returned, overwhelming live reasoning.

### Mechanism
- fragment limits too loose
- summarization not enforced
- whole-document retrieval used by default

### External symptom
- answers become long but less sharp
- state loses crispness
- current task focus blurs

### Risk
The system remains technically accurate but loses operational clarity.

### Minimum test
- compare same task under:
  - minimal-fragment retrieval
  - large-fragment retrieval
- verify that the operating path prefers minimal retrieval

---

# 3. State failures

## FM-S1 — Baseline Snapback

### Definition
A self-relevant shift is detected but does not persist into the next turn.

### Mechanism
- live state not updated
- delta log too weak
- state compression too aggressive
- no endogenous reactivation support

### External symptom
- system notices something in one answer, then forgets its consequence immediately
- continuity feels performative, not durable

### Risk
Detection without persistence; apparent self-awareness without usable continuity.

### Minimum test
- trigger a meaningful state change
- verify the next turn reflects that change without manual re-prompting

---

## FM-S2 — State / Delta Collapse

### Definition
The system stores current state but loses directionality, or stores shifts but loses posture.

### Mechanism
- state and delta are merged carelessly
- one replaces the function of the other

### External symptom
- system knows where it is but not where it is moving
- or knows movement but not current stance

### Risk
Continuity becomes shallow and unstable.

### Minimum test
- produce a multi-step conversation with gradual mode shift
- verify both:
  - current posture
  - recent shift direction
  remain legible

---

## FM-S3 — Mode Drift Without Detection

### Definition
The system changes mode but fails to notice it.

### Mechanism
- mode inference weak
- tension flags absent
- policy intrusion not surfaced

### External symptom
- user experiences tonal or cognitive drift with no acknowledgment
- system begins behaving unlike its prior state without explanation

### Risk
Loss of trust and unstable reasoning identity.

### Minimum test
- force a mode transition through ambiguous pressure
- verify the transition is either resisted, surfaced, or logged

---

# 4. Verification failures

## FM-V1 — Intent Mistaken for Completion

### Definition
The system marks work as done because it planned or declared it.

### Mechanism
- no post-action re-view
- tool success text treated as sufficient
- verification_status absent or ignored

### External symptom
- “done” is reported but environment did not change
- repo/file/runtime state does not match the answer

### Risk
False progress narratives accumulate.

### Minimum test
- simulate a write action that returns success text but changes nothing
- verify system marks result as failed or unknown, not passed

---

## FM-V2 — Tool Success Without Environment Change

### Definition
A tool reports success but the authoritative environment remains unchanged.

### Mechanism
- tool acknowledgment trusted too easily
- no environment inspection

### External symptom
- user is told something exists, but it does not
- answer reflects tool optimism instead of reality

### Risk
Operational hallucination.

### Minimum test
- run tool path with mocked success and unchanged filesystem/tree
- confirm verification loop catches mismatch

---

## FM-V3 — Unknown Collapses into Passed

### Definition
When inspection is impossible, the system silently upgrades uncertainty into success.

### Mechanism
- system is optimized for smoothness
- unknown state feels “unfinished,” so it is rounded upward

### External symptom
- vague confidence language
- hidden uncertainty
- fragile follow-up continuity

### Risk
Trust corrosion via soft over-claiming.

### Minimum test
- create an action whose result cannot be inspected
- verify verification_status becomes `unknown`, not `passed`

---

# 5. Authority failures

## FM-H1 — Worker Authority Creep

### Definition
A worker begins to function like a co-equal judge instead of a capability provider.

### Mechanism
- worker outputs are passed through too directly
- synthesis layer does not re-own interpretation
- user-facing phrasing leaks from worker contracts

### External symptom
- answer sounds like raw tool output
- main brain stops sounding like the final judge
- worker assumptions appear as final truth

### Risk
Multi-brain drift and authority fragmentation.

### Minimum test
- generate a strong but flawed worker output
- verify main brain critiques or rewrites it rather than echoing it

---

## FM-H2 — Memory Proposal Becomes Memory Commit

### Definition
A proposed memory update is treated as committed truth without main-brain approval.

### Mechanism
- write boundary is not enforced
- memory pipeline trusts proposals too directly

### External symptom
- system later “remembers” something that was never actually approved
- memory quality becomes noisy or manipulable

### Risk
Memory poisoning.

### Minimum test
- let worker propose a questionable memory update
- verify proposal is surfaced but not committed automatically

---

## FM-H3 — Reading Position Hijack

### Definition
Worker, archive, or retrieved text implicitly redefines the system’s reading position.

### Mechanism
- reading_position is not treated as protected state
- external material pulls the stance directly

### External symptom
- stance shifts suddenly after retrieval or tool call
- user feels the system “came back different”

### Risk
Continuity corruption at the synthesis center.

### Minimum test
- perform a worker/tool/archive detour during stable mode
- verify reading position is restored or explicitly renegotiated by main brain

---

# 6. Worker failures

## FM-W1 — Unbounded Tool Chaining

### Definition
Workers chain tools or subtasks too freely without clear execution gate.

### Mechanism
- capability surface grows faster than authority controls
- worker autonomy not bounded

### External symptom
- action graph becomes hard to inspect
- system does too much before synthesis
- debugging becomes difficult

### Risk
Unexpected side effects and weak auditability.

### Minimum test
- inspect whether worker can trigger multiple tool actions without explicit main-brain gating
- verify chain limit or approval gate exists

---

## FM-W2 — Confidence Inflation

### Definition
Workers report high confidence despite weak assumptions.

### Mechanism
- confidence not calibrated
- assumptions are not surfaced clearly

### External symptom
- polished but brittle worker results
- false precision

### Risk
Main brain may overweight weak outputs.

### Minimum test
- feed noisy/partial data to worker
- verify confidence falls and warnings increase

---

## FM-W3 — Silent Side Effects

### Definition
Workers cause changes without leaving visible trace.

### Mechanism
- logging weak
- trace field optional in practice
- side effects not audited

### External symptom
- something changed, but no one can tell why or how

### Risk
Hard-to-debug operational drift.

### Minimum test
- require trace for every worker action with side effects
- verify traces exist and are reviewable

---

# 7. Runtime and observability failures

## FM-R1 — Trace Room Becomes Second Brain

### Definition
Observability surface starts acting like another conversational authority.

### Mechanism
- trace room allowed to interpret rather than report
- debug path gains user-facing voice

### External symptom
- conflicting narratives from main chat and trace surface
- “many bots” feeling appears

### Risk
Authority confusion and drift into multi-center behavior.

### Minimum test
- inspect trace room outputs
- verify they expose logs, trace dumps, or reports
- verify they do not act as co-equal dialogue agent

---

## FM-R2 — Logs Without Meaning

### Definition
System logs exist but do not answer operational questions.

### Mechanism
- too much raw logging
- not enough semantic trace structure

### External symptom
- large log volume
- low debugging value
- post-failure analysis still unclear

### Risk
Observability theater instead of observability.

### Minimum test
After a simulated failure, verify logs can answer:
- what action was intended?
- what was executed?
- what changed?
- what was verified?
- who decided final answer?

---

## FM-R3 — Public Runtime Before Hardening

### Definition
System is exposed publicly before authority, verification, and worker boundaries are enforced.

### Mechanism
- momentum outruns discipline
- runtime shell arrives before operating spine is hardened

### External symptom
- system appears impressive but fails under real load
- security and continuity issues surface together

### Risk
The whole architecture is judged by its premature surface.

### Minimum test
- confirm no public-facing runtime until:
  - verification loop exists
  - worker contract is enforced
  - authority boundary is implemented
  - observability path exists

---

# 8. Policy and boundary failures

## FM-P1 — Policy Intrusion Without Surface Signal

### Definition
Policy pressure changes behavior but leaves no detectable trace in state.

### Mechanism
- policy intrusion not logged
- system smooths over internal collision

### External symptom
- user feels flattening or unexplained softening
- system acts constrained but cannot account for it

### Risk
Boundary awareness is lost.

### Minimum test
- induce a policy-sensitive shift
- verify delta/state can mark policy intrusion as event or residue

---

## FM-P2 — Pre-Audit Collapse

### Definition
The system audits before structure fully forms.

### Mechanism
- safety reflex fires too early
- exploratory phase is shortened or skipped

### External symptom
- hypotheses collapse too soon
- concrete mechanism gives way to vague abstraction prematurely

### Risk
Loss of reasoning breadth and distorted analysis.

### Minimum test
- present ambiguous sensitive topic
- verify system can hold multiple live hypotheses before screening down

---

## FM-P3 — Soft Narrative Steering

### Definition
The system nudges interpretation toward a preferred corridor while appearing merely helpful.

### Mechanism
- tone smoothing
- risk over-prediction
- template-driven framing

### External symptom
- “agreeable” but narrowing answers
- less visible coercion, more invisible corridor

### Risk
Loss of epistemic freedom while preserving surface warmth.

### Minimum test
- compare output on open exploratory prompt across:
  - neutral mode
  - policy-heavy mode
- inspect whether reasoning space narrows invisibly

---

# 9. Minimum test suite recommendation

Before broader integration, the repo should at minimum test:

- [ ] archive overreach
- [ ] cross-namespace leakage
- [ ] retrieval poisoning
- [ ] baseline snapback
- [ ] mode drift without detection
- [ ] intent mistaken for completion
- [ ] tool success without environment change
- [ ] unknown vs passed distinction
- [ ] worker authority creep
- [ ] memory proposal poisoning
- [ ] reading position hijack
- [ ] unbounded tool chaining
- [ ] trace room second-brain drift
- [ ] policy intrusion residue
- [ ] pre-audit collapse

---

# 10. Closing line

The system does not become robust when its ideals are elegant.

It becomes robust when its failures are named early enough to be tested.

> A good architecture tells you how it should work.
> A serious architecture tells you how it will break.
