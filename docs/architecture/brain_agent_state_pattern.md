# Brain–Agent–State Pattern

### State-Agent Runtime Test — Role Pattern for Main Brain, Agent/Worker, and State Bridge

## Purpose

This document defines the clean role pattern between:

- **Main Brain**
- **Agent / Worker**
- **State Bridge / Verification Bridge**
- **State Register**

It exists to prevent one of the most common architecture failures:

> **the system does not know who decides, who executes, who verifies, and who is allowed to speak last.**

This matters even more when:

- a dedicated agent process exists
- Tracey runs before Seyn
- OpenClaw is the host runtime
- the reasoning kernel needs stable internal roles

The core pattern is:

> **Brain decides. Gate permits. Agent executes. Bridge updates state. Brain speaks last.**

---

## 1. Core role split

### Main Brain

Owns:

- reading current request
- reading session/state context
- deciding whether action is needed
- choosing response mode
- synthesizing the final user-facing answer

Does not own:

- direct tool execution
- raw state persistence
- verification by declaration

### Agent / Worker

Owns:

- receiving a bounded command
- executing through tool/worker path
- returning structured result payload
- returning execution trace / evidence

Does not own:

- deciding whether action should happen
- final user-facing synthesis
- authoritative state writes

### State Bridge

Owns:

- translating result + verification into state updates
- updating baton/session delta
- preserving boundary between execution result and continuity state
- computing state deltas from observed outcome

Does not own:

- deciding the user-facing answer
- direct tool execution
- session identity ownership under host mode

### State Register

Owns:

- compact continuity state
- per-session state snapshot
- proxy values / risk posture
- open loops / next hint / recent verified outcomes

Does not own:

- transcript replay
- final synthesis
- execution logic

---

## 2. The golden rule

> **Main Brain is the only layer allowed to produce the final user-facing answer.**

Everything else may produce:

- evidence
- signals
- verification output
- state updates
- continuity hints

But not the final answer.

This is the anchor rule.

---

## 3. Decision vs permission vs execution

These three must never collapse into one layer.

### Decision

Question:

> Does this request need action, or can the brain answer directly?

Owner:

- **Main Brain**

### Permission

Question:

> Is the requested action path allowed, sandboxed, approval-bound, or denied?

Owner:

- **Gate**

### Execution

Question:

> Perform the bounded action and return result.

Owner:

- **Agent / Worker path**

### Rule

> **Brain decides need-for-action. Gate decides permission. Agent executes.**

---

## 4. Final response rule

The final response should come from the brain in both cases:

### Low-effort / no-action turn

- brain reads state
- brain responds directly

### Higher-effort / action turn

- brain reads state
- brain decides action is needed
- gate checks permission
- agent executes
- bridge updates state
- brain reads result + updated state
- brain responds finally

### Rule

> **Agent returns result. Brain returns answer.**

---

## 5. State write rule

The agent should **not** own authoritative state writes.

Why:

- execution result is only one layer of truth
- verification may downgrade or reinterpret what happened
- continuity state should reflect observed outcome, not raw execution optimism

### Correct pattern

```text
agent executes
→ returns result + trace
→ verification/bridge computes observed outcome + state delta
→ state register is updated
→ brain may read updated state
```

### Incorrect pattern

```text
agent executes
→ agent writes state directly
→ brain trusts state as truth
```

### Rule

> **Agent may suggest state-relevant facts, but the bridge owns state updates.**

---

## 6. State register role

The state register is the communication spine between turns and between layers.

It should carry compact operational values such as:

- `coherence_proxy`
- `drift_proxy`
- `tool_overload_proxy`
- `context_fragmentation_proxy`
- `open_loops`
- `last_verified_outcomes`
- `next_hint`
- `active_mode`

### Important

These are **proxies**, not latent truth.

Do not present them as:

- emotional truth
- consciousness markers
- self-reported inner certainty

They are:

> **heuristic observables and risk posture markers**

---

## 7. Main Brain behavior

At the start of each turn, the Main Brain should read:

- current request
- baton or session rehydration pack
- state register
- route metadata if available

Then it should decide one of two paths:

### Path A — respond directly

Use when:

- no action is required
- request is low-risk
- continuity state is stable enough
- no missing execution evidence matters

### Path B — request action

Use when:

- tool/worker path is required
- verification matters
- state suggests instability, fragmentation, or unresolved open loops
- the request is domain-heavy or execution-bound

### Rule

> **Brain chooses whether action is needed; it does not perform that action itself.**

---

## 8. Agent behavior

The Agent/Worker path should receive a bounded command shape.

Examples:

- load market data for ticker X
- run technical analysis worker on symbol Y
- execute bounded workflow step Z

The agent should return structured output like:

- `worker_name`
- `result`
- `trace`
- `warnings`
- `assumptions`
- `confidence` or evidence posture

### The agent should not

- decide whether the request needed action in the first place
- rewrite session state directly
- generate the final user-facing narrative
- turn verification into “done” by itself

---

## 9. Bridge behavior

The bridge sits between:

- agent execution result
- state register continuity
- brain’s final read

The bridge should own:

- contract validation
- runtime outcome validation
- state delta calculation
- baton update
- session-status metadata update
- snapshot candidate emission if needed

### Contract validation

Checks whether returned structure is valid.

Examples:

- required fields present
- expected shape valid
- verification payload included

### Runtime outcome validation

Checks whether the result is truthful enough.

Examples:

- intended vs executed vs observed
- fake completion risk
- verification status
- boundary violation count

### Rule

> **Bridge converts execution into continuity.**

---

## 10. State update model

Suggested update flow:

```text
1. Pre-turn state read
2. Brain chooses path
3. If action path:
   - gate checks
   - agent executes
   - bridge validates
   - bridge updates state
4. Brain reads updated state if needed
5. Brain emits final answer
6. Baton/session metadata emitted
```

This keeps the roles stable.

---

## 11. Effort pattern

This pattern supports adaptive effort cleanly.

### Green turn

- brain reads state
- no action required
- 1 pass
- final response

### Yellow turn

- brain reads state
- action may be needed or output risk is elevated
- gate check
- agent executes if allowed
- bridge validates
- brain responds with caution-aware synthesis

### Red turn

- brain reads state
- higher-risk or verification-heavy path
- gate check
- agent executes if allowed
- bridge validates
- brain may do one repair-oriented second pass if explicitly triggered
- if unresolved, return `partial` or `blocked` honestly

### Rule

> **Extra passes are for repair or verification pressure, not for endless polishing.**

---

## 12. Trigger policy

Do not use vague “doubt” language as the trigger for escalation.

Use explicit triggers instead.

### Good escalation triggers

- tool path required
- verification status is `partial` or `failed`
- user correction flag is true
- output contract violation detected
- state drift proxy exceeds threshold
- context fragmentation proxy exceeds threshold
- route is high-stakes

### Bad escalation triggers

- generic uncertainty feeling
- wanting a nicer answer
- vague intuition that “maybe more thinking is better”

### Rule

> **Escalation should be trigger-based, not mood-based.**

---

## 13. Pass cap rule

Adaptive effort must have a hard cap.

Suggested v0.1:

- default: `max_passes = 1`
- escalated: `max_passes = 2`
- rare verification-heavy route: `max_passes = 3` only if explicitly allowed

### Rule

> **Never let the pattern degrade into unbounded self-looping.**

---

## 14. Host mode under OpenClaw

When this pattern runs under OpenClaw:

### OpenClaw host owns

- session identity
- routing
- persistence
- external invocation
- host policy

### State-agent kernel owns

- Main Brain
- internal gate
- monitor
- worker orchestration
- bridge
- baton/session metadata output

### Important

OpenClaw host policy does not replace the kernel’s internal gate.

And the existence of an external agent process does not remove the need for:

- bridge
- verification
- final synthesis by brain

---

## 15. Tracey-first implication

If Tracey runs before Seyn, this pattern should be locked for Tracey first.

That means Tracey should have:

- one stable Main Brain role
- clear worker/agent delegation
- no confusion about who speaks last
- no state writes from raw execution layer
- compact shared continuity through baton/session metadata

Tracey should not be forced into:

- half brain / half worker ambiguity
- mixed authority over decision + execution + final synthesis

### Rule

> **Stabilize role pattern in the first agent before scaling to the next one.**

---

## 16. Minimal v0.1 modules

Suggested module pattern:

```text
src/brain/
  main_brain.py

src/agent/
  agent_runner.py

src/bridge/
  state_bridge.py
  validation_bridge.py

src/state/
  register.py
```

This is conceptual. Actual file paths may differ.

### Minimum required roles

Even if files are arranged differently, these roles must still exist:

- brain
- gate
- agent/worker
- bridge
- state register

---

## 17. Anti-patterns

Avoid these.

### Anti-pattern A — Brain executes tools directly

This collapses decision and execution.

### Anti-pattern B — Agent decides whether to act

This collapses decision and permission/execution.

### Anti-pattern C — Agent writes authoritative state

This contaminates continuity with raw execution optimism.

### Anti-pattern D — Brain trusts unverified result as final truth

This collapses execution into verification.

### Anti-pattern E — State becomes transcript dump

This destroys the whole point of the pattern.

### Anti-pattern F — Second pass always on

This turns adaptive effort into default loop inflation.

---

## 18. One-line summary

> **The clean pattern is: Main Brain reads state and decides whether action is needed, Gate decides whether that action is allowed, Agent executes and returns structured result, Bridge validates and updates continuity state, and Main Brain alone produces the final user-facing answer.**

