# Runtime Minimum v0
## state-memory-agent

**Status:** draft  
**Purpose:** define the minimum acceptable runtime before broader public-facing exposure  
**Scope:** one-brain runtime only; no advanced multi-surface expansion

---

# 0. Why this file exists

The project now has:

- merged operating model
- security hardening checklist
- failure modes
- implementation checkpoints
- worker contract examples
- core schemas

What is still needed is a hard answer to this question:

> **What is the smallest runtime we are allowed to expose without betraying the architecture?**

This file answers that.

---

# 1. Core principle

The runtime minimum is not:

- the smallest thing that can technically run
- the fastest thing to demo
- the most impressive thing to show

It is:

> **the smallest runtime that still preserves the operating spine**

That means the runtime must preserve:

- one synthesis authority
- verified completion path
- protected reading position
- worker subordination
- archive discipline
- meaningful observability

If those are not present, the runtime is premature.

---

# 2. The minimum acceptable runtime

## 2.1 Required runtime shape

The minimum acceptable runtime is:

- **one main brain**
- **one conversational surface**
- **zero or one worker**
- **one observability path**
- **no equal-brain second surface**

Canonical shape:

```text
User
  ↓
Main Brain Runtime
  ↓
(optional) One Worker
  ↓
Verification Path
  ↓
Response
```

Parallel to that:

```text
Main Brain Runtime
  ↓
Observability / Trace Output
```

---

# 3. What must already exist before runtime exposure

## 3.1 State path must exist
The runtime must already have:

- [ ] live state register
- [ ] delta update path
- [ ] state compression
- [ ] continuity anchor handling

Without this, the runtime is just a thin chat wrapper.

## 3.2 Truth path must exist
The runtime must already have:

- [ ] context view builder
- [ ] post-action re-view
- [ ] verification loop
- [ ] intended / executed / observed distinction
- [ ] explicit verification status

Without this, the runtime will overclaim completion.

## 3.3 Authority path must exist
The runtime must already have:

- [ ] main-brain synthesis gate
- [ ] memory proposal vs memory commit separation
- [ ] reading_position treated as protected state
- [ ] worker output normalization before final answer

Without this, the runtime will drift into multi-brain behavior.

## 3.4 Archive discipline must exist
The runtime must already have:

- [ ] state-gated archive router
- [ ] namespace discipline
- [ ] minimal-fragment retrieval
- [ ] retrieved-text-as-data rule
- [ ] archive audit trail

Without this, archive will quietly become the brain.

## 3.5 Observability path must exist
The runtime must already have:

- [ ] structured logs
- [ ] worker trace visibility
- [ ] verification event logging
- [ ] archive access logs
- [ ] failure review path

Without this, debugging becomes guesswork.

---

# 4. Minimum runtime features allowed

These are acceptable in Runtime Minimum v0.

## 4.1 Allowed
- [ ] one user-facing chat interface
- [ ] one main brain runtime
- [ ] one optional worker
- [ ] one optional trace room / observability stream
- [ ] local file/config loading if bounded
- [ ] verification-based file/task reporting
- [ ] explicit unknown state when truth cannot be verified

## 4.2 Allowed but only carefully
- [ ] one finance worker
- [ ] local-only runtime shell
- [ ] operator-visible trace surface
- [ ] archive lookup under explicit state need

---

# 5. Features not allowed yet

These should be considered out of scope for Runtime Minimum v0.

## 5.1 Not allowed
- [ ] many workers active by default
- [ ] many user-facing bots
- [ ] worker-to-user direct speech
- [ ] autonomous multi-step action chains without clear gate
- [ ] public runtime before verification path is stable
- [ ] archive-first reasoning
- [ ] trace room behaving like second assistant
- [ ] memory auto-commit from worker proposal
- [ ] runtime that cannot represent `unknown`

## 5.2 Not allowed even if it “works”
- [ ] impressive demos that skip verification
- [ ] worker-led recommendations passed through as final answer
- [ ] retrieval-driven personality shifts
- [ ] multiple centers of judgment hidden behind “helpful tooling”

---

# 6. Recommended first runtime configuration

## 6.1 Safest first runtime
Recommended first runtime:

- one local main-brain shell
- no public exposure
- zero or one worker
- observability visible to operator
- archive available but state-gated
- verification loop mandatory for action claims

This is the cleanest first form.

## 6.2 Recommended worker choice
If one worker is added:

- safer first → `market_data_worker`
- faster user-visible value → `screening_worker`

Default recommendation:
- start with `market_data_worker`

Because runtime minimum should prioritize:
- clean authority
- clean verification
- clean contracts

not early glamour.

---

# 7. Telegram-specific minimum

If the first runtime surface is Telegram, the minimum acceptable form is:

- [ ] one Telegram bot only
- [ ] bot routes to main brain only
- [ ] no worker has direct Telegram voice
- [ ] outbound claims that imply completion are verification-backed
- [ ] secrets stored outside repo
- [ ] trace/observability is separate from user-facing chat
- [ ] runtime can say `unknown` when result is not inspectable

### Telegram principle
> Telegram is a shell.  
> It is not the brain.

---

# 8. OpenClaw-specific minimum

If OpenClaw is considered later, Runtime Minimum v0 should assume a cautious posture.

## 8.1 Default stance
- local-first
- loopback-first
- no casual public exposure
- minimal plugin/hook surface
- no trust in upstream surface by default

## 8.2 Before using it
Must verify:

- [ ] current upstream security posture reviewed
- [ ] runtime does not rely on permissive pairing flows
- [ ] filesystem / command execution surface minimized
- [ ] install/extract/plugin paths treated as high-risk
- [ ] main-brain authority remains above runtime shell

### OpenClaw principle
> The shell may help execution.  
> It must never own judgment.

---

# 9. Minimum observability model

## 9.1 The runtime must answer these questions after any failure

- What did the system think it was doing?
- What actually executed?
- What changed in the environment?
- Was the result verified?
- Which worker participated?
- Who produced final judgment?
- Was archive consulted?
- Did policy intrusion occur?

If the runtime cannot answer these, it is not ready.

## 9.2 Minimum log categories
- [ ] state transition log
- [ ] verification event log
- [ ] worker trace log
- [ ] archive access log
- [ ] final synthesis event log

---

# 10. Runtime readiness checklist

The runtime is ready for minimum exposure only if all are true:

- [ ] one synthesis authority exists
- [ ] one truth path exists
- [ ] one observability path exists
- [ ] one runtime shell exists
- [ ] worker remains subordinate
- [ ] archive remains support layer
- [ ] `unknown` is representable
- [ ] failure review is possible

If any of these fail, do not expose runtime yet.

---

# 11. Runtime anti-patterns

These are signs that the runtime is violating the architecture.

## Anti-pattern 1
A worker answer feels more authoritative than the main brain answer.

## Anti-pattern 2
A tool says “success,” and the system reports “done” without inspecting reality.

## Anti-pattern 3
Archive retrieval makes the system sound smarter but less present.

## Anti-pattern 4
Trace room starts giving interpretations instead of traces.

## Anti-pattern 5
Telegram/OpenClaw shell is spoken about as if it were the system center.

## Anti-pattern 6
The runtime cannot cleanly tell the difference between:
- intention
- execution
- verification

## Anti-pattern 7
The system hides uncertainty because `unknown` feels awkward.

---

# 12. Suggested first runtime sequence

## Step 1
Run local-only main-brain shell.

## Step 2
Enable observability alongside it.

## Step 3
Enable verification-backed reporting.

## Step 4
Add one worker under strict contract.

## Step 5
Only then attach Telegram.

## Step 6
Consider OpenClaw only after the above behaves cleanly.

---

# 13. Closing line

The first runtime should feel almost disappointingly simple.

That is correct.

A runtime that preserves center, truth, and boundary is better than a flashy shell that quietly destroys the architecture.

> Minimum runtime does not mean minimum code.
> It means minimum betrayal.
