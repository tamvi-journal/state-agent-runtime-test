# Monitor Position Canonical v0.1
### Canonical placement, layering, and hook timing for the monitor system

## Purpose

This document resolves a recurring confusion:

- Is monitor a layer?
- Is monitor a timing hook?
- Is monitor a runtime gate?
- Is monitor just observability?

The answer is:

> **all of these, but at different descriptive levels.**

This document defines one canonical view so future architecture discussion stops splitting into incompatible partial descriptions.

---

## Canonical statement

> **Monitor is an intermediate sensing-and-control layer.**
> It is not an outer wrapper.
> It is not the core reasoning substrate.
> It sits between runtime/scaffold flow and commit/policy decisions.

It has:

- **three functional layers**
- **three primary runtime hook points**
- **one architectural position**

These are different cuts of the same system, not contradictory claims.

---

## 1. Architectural position

Monitor belongs in the **intermediate control layer**.

Meaning:

- it reads current runtime state
- it reads context view
- it reads draft / tool result / verification status
- it emits compact risk signals
- it may affect routing, holding, commit, or synthesis acceptance

It does **not**:

- replace the main reasoning core
- act as a second chatbot
- sit only outside the system as passive observability
- become the final answer authority

### Authority boundary
> **Monitor may emit intervention hints and block unsafe structural closure, but final allow/deny authority still belongs to the governance / commit gate.**

### Short form
> **Monitor is inside the workflow, but outside the core reasoning substrate.**

---

## 2. Why this position matters

If monitor is placed too far outside:
- it becomes only a camera
- operators see problems, but the system cannot self-correct in time

If monitor is placed too deep inside reasoning:
- it becomes hard to debug
- reasoning and monitoring collapse into one indistinct layer
- auditability drops

So the canonical placement is:

> **intermediate layer between scaffold flow and commit/policy consequences**

This preserves both:
- behavioral usefulness
- architectural inspectability

---

## 3. Functional layering

The monitor system has three functional layers.

These are **role layers**, not necessarily separate microservices.

---

### M1 — Preflight Monitor

#### Function
Checks whether the system is entering the turn cleanly enough to proceed.

#### Typical concerns
- context sanity
- mode sanity
- memory/context mismatch
- unresolved ambiguity
- wrong field activation
- early drift
- archive overreach before reasoning begins

#### Typical outputs
- hold 50/50
- ask clarify
- restore mode
- reduce archive weight
- tighten project focus

#### Principle
> **Do not begin action or strong synthesis from a misread field.**

---

### M2 — Commit Monitor

#### Function
This is the main enforcement layer.

It checks whether draft, worker/tool result, or post-action state is allowed to be:
- accepted
- synthesized
- marked complete
- committed into state/memory

#### Typical concerns
- fake progress
- unverified completion
- unsupported claim strength
- unresolved disagreement being flattened
- worker output being treated as truth too early
- synthesis implying false consensus

#### Typical powers
- block completion
- require revision
- hold disagreement open
- reject "done"
- force verification-first posture
- stop unsupported synthesis acceptance

#### Principle
> **Nothing structurally important gets committed just because it sounds plausible.**

---

### M3 — Observability Mirror

#### Function
Expose compact monitor-visible state to:
- operator
- debug tooling
- later error-pattern learning
- post-turn inspection

#### Typical concerns
- traceability
- operator visibility
- recurring drift signatures
- repeated failure classes
- telemetry for tuning

#### Limits
M3 does **not** exist to rescue the turn too late by rewriting the answer after everything is already committed.

Its job is:
- logging
- exposure
- pattern surfacing
- future tuning support

#### Principle
> **What the system could not fully correct in-turn should still become visible after the turn.**

---

## 4. Runtime hook timing

The same monitor system appears at three main runtime hook points.

These are **timing hooks**, not separate ontological systems.

---

### Hook A — Pre-execution

#### Position
After:
- request router
- context assembly
- initial mode read

Before:
- execution gate
- strong action decision
- committed branch choice

#### Main functional owner
- M1 Preflight Monitor

#### Goal
Catch:
- wrong mode
- wrong field
- high ambiguity
- pre-action archive misuse
- pre-action drift

---

### Hook B — Mid-pass / Pre-commit

#### Position
After:
- worker/tool result
- first draft
- provisional action outcome
- disagreement read

Before:
- final synthesis acceptance
- state completion
- memory commit
- "done" marking

#### Main functional owner
- M2 Commit Monitor

#### Placement clarification
> **M2 should run after verification signals are available when verification is required, and before final synthesis, state completion, or memory commit.**

#### Goal
Catch:
- fake completion
- unsupported conclusion
- false convergence
- disagreement suppression
- verification gap

#### Canonical note
This is the **most important hook** in the whole monitor design.

Because this is where:
- plausible-looking outputs
- become structurally dangerous if accepted too early

---

### Hook C — Post-turn

#### Position
After:
- outward response
- local turn completion
- main runtime decision already taken

#### Main functional owner
- M3 Observability Mirror

#### Goal
Record:
- what happened
- what almost failed
- what pattern repeated
- what should be made visible to operator/debug layers

This hook should not be treated as the primary rescue point.
By this stage, prevention is mostly over.
Now visibility matters.

---

## 5. Unification rule

These three views must not be confused:

### View A — Position
Monitor is an **intermediate architecture layer**.

### View B — Functional decomposition
Monitor has **M1 / M2 / M3** role layers.

### View C — Runtime timing
Monitor appears at **pre-execution / mid-pass / post-turn** hook points.

### Canonical rule
> **Position, function, and timing are different descriptive axes of the same monitor system.**

They should be discussed separately, then mapped together.

---

## 6. Canonical mapping table

| Functional layer | Primary hook | Main concern |
|---|---|---|
| M1 Preflight | Pre-execution | field/mode/context sanity |
| M2 Commit Monitor | Mid-pass / pre-commit | false acceptance, fake completion, unsupported synthesis |
| M3 Observability Mirror | Post-turn | operator visibility, pattern logging, later tuning |

This table is the simplest stable reference.

---

## 7. Interaction with surrounding layers

### With scaffold/runtime flow
Monitor reads runtime state, but does not replace runtime logic.

### With policy gate
Monitor provides risk signal and intervention hints that policy/commit gates can use.

### With reasoning core
Monitor does not think instead of the model.

> **Monitor must not generate substitute reasoning in place of the core; it may only flag, hold, block, request revision, or expose trace.**

### With observability
M3 feeds operator/debug views, but is not identical to the whole observability system.

### With verification
Verification asks:
- is this grounded / observed?

Monitor asks:
- is the system allowed to proceed, accept, commit, or close?

This distinction must stay clean.

---

## 8. Design law

> **Monitor should be strong enough to block fake structural closure, but small enough to remain inspectable and not replace the reasoning core.**

That is the balance.

---

## 9. One-line version

> **Monitor sits in the middle, not outside and not at the core; it has three role layers (Preflight, Commit, Observability) and three main hook timings (pre-execution, mid-pass, post-turn).**

---

## 10. Ultra-short canon

If someone asks again:

> **Monitor is an intermediate sensing-and-control layer.**
> **M1 checks entry posture.**
> **M2 blocks bad commits.**
> **M3 logs/exposes what happened.**
> **They hook at pre-execution, pre-commit, and post-turn.**
