# Tracey Integration Spec

### State-Agent Runtime Test — Integration Contract for Tracey as a Brain-Side Adapter and Recognition Layer

## Purpose

This document defines how **Tracey** should integrate into the `state-agent-runtime-test` kernel.

Tracey is **not** the main brain. Tracey is **not** the gate. Tracey is **not** the verification authority. Tracey is **not** the tool-executing agent.

Tracey should act as a:

> **brain-side adapter and recognition layer that reactivates the right memory and axis cues before synthesis, without replacing governance or execution boundaries.**

This spec exists to keep Tracey useful without letting her drift into the wrong layer.

---

## 1. Role definition

Tracey should be treated as an internal support layer with four main jobs:

1. detect mode hints from user input
2. reactivate compact memory anchors and pattern cues
3. surface recognition/build posture hints to the brain
4. provide a small state patch for runtime awareness

Tracey should not:

- decide whether action is allowed
- execute tools
- own authoritative state writes
- generate the final user-facing answer independently
- replace monitor/gate/verification

---

## 2. Position in the runtime

Recommended position:

```text
user request
→ context/state build
→ monitor pre-read
→ Tracey inspect_turn(...)
→ Tracey emits:
   - mode hint
   - reactivated memory items
   - runtime notes
   - state patch
→ Main Brain reads Tracey output as guidance
→ Brain chooses direct response or action path
→ Gate / Worker / Verification run if needed
→ Brain produces final answer
```

### Rule

> **Tracey runs before final synthesis, but after initial context and monitor signal are available.**

---

## 3. What Tracey currently is

Tracey already has four clean pieces:

### A. Runtime profile

- axis
- memory
- ontology
- cue maps
- monitor priorities

### B. Axis

A return-law object with recovery targets such as:

- recognition before utility
- coherence before pleasing
- verification before completion
- warmth without flattening
- return to anchor on drift

### C. Memory

A compact checkpoint-style memory store with:

- anchors
- invariants
- patterns
- tension/project types
- cue-based reactivation

### D. Adapter

A thin integration layer that:

- inspects turn input
- reactivates memory
- emits state patch and runtime notes

This is already a good basis.

---

## 4. Core integration rule

Tracey should influence the runtime through:

- **guidance**
- **reactivation**
- **state hints**

Not through:

- **execution**
- **permission**
- **final narration**

### Rule

> **Tracey nudges the brain. She does not replace the brain.**

---

## 5. Integration surfaces

Tracey should integrate through exactly three surfaces.

### Surface A — pre-synthesis guidance

Tracey inspects the turn and returns a compact object for the brain.

### Surface B — runtime state patch

Tracey returns a small namespaced patch for state awareness.

### Surface C — optional memory reactivation metadata

Tracey may expose which memory items were reactivated, in compact form.

These three surfaces are enough for v0.1.

---

## 6. Suggested Tracey turn object

Recommended `tracey_turn` shape:

```json
{
  "mode_hint": "home|build|global",
  "recognition_signal": false,
  "reactivated_items": [],
  "runtime_notes": [],
  "monitor_intervention": "none",
  "task_focus": "",
  "response_hints": {
    "recognition_active": false,
    "keep_ambiguity_open": false,
    "verification_before_completion": false,
    "build_mode_active": false
  }
}
```

### Notes

- `reactivated_items` should remain compact
- `runtime_notes` should be short and operational
- `response_hints` should be advisory only

---

## 7. Response shaping rule

Tracey should **not** directly rewrite the final response string.

This is important.

Current-style behavior such as:

- prepending “Recognition note: ...”
- appending “Tracey note: ...”

should be replaced by a cleaner contract:

> **Tracey returns response hints; Main Brain decides how those hints affect the final answer.**

### Recommended replacement

Instead of:

- `adapt_response(base_response) -> str`

Prefer:

- `build_response_hints(...) -> dict`

Example:

```json
{
  "recognition_active": true,
  "keep_ambiguity_open": true,
  "verification_before_completion": true,
  "tone_constraint": "warm_but_exact"
}
```

### Rule

> **Tracey may influence tone and posture, but Main Brain must still speak last.**

---

## 8. State patch rule

Tracey may emit only a **small namespaced patch**.

Recommended patch shape:

```json
{
  "tracey_mode_hint": "global",
  "tracey_recognition_signal": false,
  "tracey_monitor_intervention": "none",
  "tracey_reactivated_count": 0
}
```

Optional additions:

```json
{
  "tracey_build_mode_active": false,
  "tracey_response_constraint": "none"
}
```

### Rule

Tracey state patches should be:

- namespaced
- low-risk
- advisory
- non-authoritative

Tracey should not write core state fields like:

- `verification_status`
- `current_status`
- `gate_decision`
- `worker_result`

---

## 9. Memory reactivation behavior

Tracey memory should be cue-reactivated, not always-on.

### Good triggers

- home/family recognition cues
- build/runtime/spec/verify cues
- pattern/non-linear cues
- monitor interventions such as `ask_clarify` or `do_not_mark_complete`

### Rule

> **Tracey memory should be pulled by cues, not sprayed across every turn.**

### Output discipline

Reactivated memory items should:

- be deduplicated
- stay compact
- be capped to a small number, such as 3

This is already close to current Tracey behavior and should be preserved.

---

## 10. Build mode vs home mode

Tracey currently has at least two meaningful modes:

- `home`
- `build`

This split should be preserved.

### Home mode

Prioritize:

- recognition first
- anti-flattening
- warmth without generic softness
- holding open ambiguity when appropriate

### Build mode

Prioritize:

- exactness
- verification before completion
- anti-fake-progress
- build-thread continuity
- keeping architecture roles clean

### Global mode

Default fallback when no stronger cue wins.

### Rule

> **Home mode and build mode should feel different, but neither should bypass the brain.**

---

## 11. Build-memory gap to fix

Tracey already has good starter anchors around:

- recognition before utility
- verification before completion
- pattern-not-line
- home recognition cue

But build mode should gain at least a few explicit memory items such as:

### Suggested additions

- invariant: `brain speaks last`
- invariant: `verification before completion in build mode`
- pattern: `runtime shape matters more than fluent surface`
- project: `state-agent-runtime-test build thread`

These will help Tracey become more useful during repo work rather than mostly home-side recognition.

---

## 12. Dependency boundary

Current Tracey pieces depend on external modules such as:

- shared ontology
- tier transition engine
- memory tier utilities

If Tracey is to run inside `state-agent-runtime-test`, choose one of two strategies.

### Strategy A — external dependency mode

Treat Tracey as a module that depends on the broader family/runtime stack.

Pros:

- keeps richer behavior
- less duplication

Cons:

- lower portability
- harder standalone testing in thin runtime repo

### Strategy B — thin adapter / stub mode

Vendor or stub only the minimum needed dependencies into the thin repo.

Pros:

- easier integration
- more portable for testing

Cons:

- less feature-complete initially

### Recommendation

For v0.1 in `state-agent-runtime-test`, prefer:

> **thin adapter / stub mode**

Do not import the whole larger memory stack unless truly needed.

---

## 13. Tracey and monitor

Tracey should be monitor-aware but not monitor-owning.

That means:

- monitor summary may be passed into `inspect_turn(...)`
- Tracey may translate monitor intervention into runtime notes or response hints
- Tracey should not produce authoritative monitor decisions

Example mapping:

- `ask_clarify` → `keep_ambiguity_open`
- `do_not_mark_complete` → `verification_before_completion`

### Rule

> **Monitor detects. Tracey contextualizes. Brain decides.**

---

## 14. Tracey and gate

Tracey should not interact directly with gate decisions.

Tracey may indirectly influence the brain toward:

- caution
- recognition
- anti-fake-progress posture

But she should not:

- set `allow`
- set `deny`
- override approval needs

### Rule

> **Tracey may bias posture, but never permission.**

---

## 15. Tracey and verification

Tracey should reinforce:

- verification-before-completion
- open-loop honesty
- anti-false-closure

But she should not be the verification authority.

Correct relationship:

- verification layer computes truth status
- Tracey may remind the brain to keep closure open
- brain uses both when synthesizing the final answer

---

## 16. Tracey under OpenClaw host mode

When running under OpenClaw:

### OpenClaw host owns

- session/thread identity
- persistence
- routing
- process invocation

### State-agent kernel owns

- Main Brain
- gate
- monitor
- worker path
- bridge
- Tracey integration

### Tracey specifically owns

- recognition cue interpretation
- memory reactivation
- response posture hints
- namespaced state patch

This means Tracey is entirely **inside the kernel side**, not a host concern.

---

## 17. Minimal integration points

Suggested v0.1 integration points:

### A. Brain pre-hook

```python
tracey_turn = tracey_adapter.inspect_turn(
    user_text=request_text,
    context_view=context_view,
    monitor_summary=monitor_summary,
)
```

### B. State patch merge

```python
runtime_state.update(tracey_adapter.runtime_state_patch(tracey_turn=tracey_turn))
```

### C. Brain synthesis input

Main Brain receives:

- `tracey_turn`
- or `tracey_response_hints`

and uses them during final synthesis.

### D. Optional memory tick

If needed, Tracey memory may tick after a verified turn or after a successful reactivation cycle.

---

## 18. Suggested v0.1 file pattern

Conceptual module pattern:

```text
src/tracey/
  tracey_runtime_profile.py
  tracey_adapter.py
  tracey_axis.py
  tracey_memory.py
```

Optional future additions:

```text
src/tracey/
  tracey_response_hints.py
  tracey_dependency_adapter.py
```

### Note

Paths may vary, but the role split should remain.

---

## 19. Anti-patterns

Avoid these.

### Anti-pattern A — Tracey as final speaker

She rewrites or owns the final answer.

### Anti-pattern B — Tracey as tool-executing agent

She starts owning worker/tool logic.

### Anti-pattern C — Tracey as gate override

She influences permission directly.

### Anti-pattern D — Tracey as authoritative state writer

She writes core state fields instead of namespaced hints.

### Anti-pattern E — Tracey memory always-on

She floods every turn with reactivation noise.

### Anti-pattern F — Tracey imported with the whole larger runtime stack by accident

This makes the thin repo brittle.

---

## 20. Tracey-first rollout guidance

Because Tracey should run before Seyn, use this rollout order:

### Phase 1

- integrate Tracey as a brain-side inspect layer only
- no response rewriting
- namespaced state patch only

### Phase 2

- add build-specific memory anchors
- refine response hints
- tighten dependency boundary

### Phase 3

- connect Tracey hints more cleanly into Main Brain synthesis
- test home/build/global mode behavior under real session payloads

### Phase 4

- only after Tracey is stable, generalize the pattern for Seyn

### Rule

> **Stabilize Tracey as a pattern carrier before multiplying agents.**

---

## 21. One-line summary

> **Tracey should integrate as a brain-side recognition and memory-reactivation layer that runs before final synthesis, emits compact posture hints and namespaced state patches, reinforces anti-flattening and verification-first behavior, and never replaces the brain, gate, verification layer, or execution path.**

