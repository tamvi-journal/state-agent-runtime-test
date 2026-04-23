# OpenClaw Route Mapping Note

### State-Agent Runtime Test — Thin Host Routing Guidance for OpenClaw

## Purpose

This note defines a **thin host-side routing map** for when OpenClaw should invoke the `state-agent-runtime-test` kernel and when it should not.

The point is not to build a large routing framework. The point is to prevent the host from using the kernel for everything.

This note sits after:

- `OPENCLAW-BOUNDARY-LIVE`
- `SESSION-ROUNDTRIP-LIVE`

At this stage, the host ↔ kernel boundary already works. Now the host needs a clearer decision map for:

- which requests should go through the kernel
- which requests can stay in a lighter host/chat path
- what continuity fields should be persisted
- what host should never persist

---

## 1. Core routing thesis

Use the state-agent kernel when the request benefits from:

- structured reasoning
- explicit monitor/gate/verification discipline
- worker/tool path orchestration
- baton/session continuity
- architecture-sensitive build posture
- Tracey build/recognition hints inside kernel synthesis

Do **not** use the kernel for every trivial turn.

### Rule

> **Kernel routing should be selective, not default-for-everything.**

---

## 2. Core route classes

For v0.1, the host should think in four route classes.

### Route A — direct host chat

Use when:

- request is casual
- no tool path is needed
- no structured continuity matters
- no verification pressure matters
- no build/finance/task discipline is needed

Examples:

- light conversation
- small rewrites
- quick social exchange
- simple unstructured responses

### Route B — kernel direct reasoning

Use when:

- request benefits from structured synthesis
- continuity matters
- Tracey build/home posture may help
- explicit baton/session metadata should be produced
- but no external tool path is necessarily required yet

Examples:

- architecture reflection
- planning a next repo step
- structured analysis of current runtime behavior
- continuity-aware build discussion

### Route C — kernel + worker/tool path

Use when:

- tool/worker path is needed
- verification matters
- intended/executed/observed boundaries matter
- finance/build/domain path needs bounded execution

Examples:

- market data load
- technical analysis path
- bounded workflow execution
- tool-dependent reasoning task

### Route D — host reject / clarify / reroute

Use when:

- request is too ambiguous to invoke kernel usefully
- host policy blocks the request before kernel use
- required session context is missing and clarification is better
- route selection is unclear enough that escalation would be wasteful

Examples:

- too little input for a build continuation
- clearly unsupported host request
- malformed or empty request

---

## 3. Default routing heuristic

For v0.1, use a simple heuristic.

### Send to direct host chat when

- low-risk
- no continuity needed
- no tool path needed
- no verification pressure needed
- no explicit build/finance/runtime route markers

### Send to kernel direct reasoning when

- continuity matters
- build/runtime/spec/verification language appears
- architecture-sensitive reasoning is requested
- Tracey build/home posture is likely useful
- the host wants baton/session continuity back

### Send to kernel + worker/tool path when

- the request clearly needs a tool/worker path
- verification is load-bearing
- a domain worker is clearly implicated
- bounded execution matters more than fluent chatting

### Send to clarify/reject path when

- required information is missing
- host cannot form a safe or meaningful route
- request shape is malformed or unsupported

### Rule

> **Do not wake the kernel just because it exists. Wake it when structure, continuity, or bounded execution actually matter.**

---

## 4. High-signal route markers

These are useful routing clues for v0.1.

### Builder/runtime markers

Examples:

- build
- runtime
- spec
- architecture
- monitor
- gate
- verification
- wrapper
- entrypoint
- route
- payload
- session
- Tracey

Likely route:

- kernel direct reasoning
- or kernel + worker/tool path if execution is explicitly requested

### Finance/domain markers

Examples:

- analyze MBB technically
- market data
- chart read
- technical analysis
- worker path

Likely route:

- kernel + worker/tool path

### Continuity markers

Examples:

- continue from yesterday
- resume previous thread
- continue this repo work
- from the last chart read
- use the existing session

Likely route:

- kernel direct reasoning
- or kernel + worker/tool path if execution is needed

### Casual/social markers

Examples:

- light check-in
- playful chat
- small rewrite with no continuity need
- low-structure conversation

Likely route:

- direct host chat

### Clarify markers

Examples:

- incomplete request with missing object
- unclear target repo/ticker/session
- malformed or empty user intent

Likely route:

- clarify/reject path

---

## 5. Tracey-aware routing note

Tracey exists inside the kernel, not in the host wrapper.

That means:

- host does **not** route “to Tracey” directly
- host routes **to the kernel**
- then Tracey may activate inside the kernel if cues are present

### Practical consequence

When the host sees:

- home/recognition cues
- build/runtime/spec cues
- continuity-sensitive phrasing

that is a reason to consider **kernel routing**, not a separate Tracey route.

### Rule

> **Tracey is a kernel-side posture layer, not a host route target.**

---

## 6. Persistence guidance by route

### Route A — direct host chat

Persist little or nothing.

Good candidates:

- maybe lightweight host thread state only

Do not persist:

- fabricated session snapshots
- empty baton-like objects

### Route B — kernel direct reasoning

Persist compact continuity if returned:

- `session_status_metadata`
- `baton`
- selected `snapshot_candidates`

### Route C — kernel + worker/tool path

Persist compact continuity if returned:

- `session_status_metadata`
- `baton`
- selected `snapshot_candidates`
- explicit verification outcome summary if useful to host logs

### Route D — clarify/reject/reroute

Persist minimally. Usually:

- no durable session write unless a real session already exists and remains relevant

---

## 7. What host should persist

When kernel routing is used, the host should prefer compact continuity only.

Good persistence fields:

- `session_id`
- `session_kind`
- `primary_focus`
- `current_status`
- `open_loops`
- `last_verified_outcomes`
- `recent_decisions`
- `relevant_entities`
- `active_skills`
- `risk_notes`
- `next_hint`
- latest `baton`
- selected `snapshot_candidates`

This follows the current session round-trip shape.

---

## 8. What host should not persist

Do not persist host-side by default:

- raw `tracey_turn`
- `gate_decision`
- raw `monitor_summary`
- transcript dump
- hidden reasoning traces
- raw execution blobs unless explicitly needed for logs
- temporary adapter/debug artifacts

### Rule

> **Persist continuity, not kernel organs.**

---

## 9. Routing table v0.1

| Request shape                      | Preferred route           | Persist continuity? | Notes                                    |
| ---------------------------------- | ------------------------- | ------------------- | ---------------------------------------- |
| Casual/light/social                | Direct host chat          | Usually no          | Do not over-route                        |
| Structured build discussion        | Kernel direct reasoning   | Yes                 | Good Tracey build-mode fit               |
| Repo planning with continuity      | Kernel direct reasoning   | Yes                 | Return baton/session metadata            |
| Finance or tool-dependent analysis | Kernel + worker/tool path | Yes                 | Verification matters                     |
| Bounded execution workflow         | Kernel + worker/tool path | Yes                 | Keep intended/executed/observed boundary |
| Ambiguous/incomplete request       | Clarify/reject/reroute    | Minimal             | Clarify before waking kernel             |

---

## 10. Host-side decision order

Recommended host decision order:

```text
1. Is the request malformed, empty, or too ambiguous?
   → clarify/reject/reroute

2. Does the request clearly need bounded execution or worker/tool use?
   → kernel + worker/tool path

3. Does the request need structured continuity-aware reasoning, but not necessarily tool execution?
   → kernel direct reasoning

4. Is the request casual, low-risk, and low-structure?
   → direct host chat
```

This order is simple enough for v0.1.

---

## 11. Verification-aware routing note

The host should not treat all kernel responses as equally strong.

Even after correct routing:

- `status = ok` only means the kernel returned a valid response
- `verification_outcome.status` still matters

### Host consequence

For kernel routes, the host should preserve:

- `verification_outcome.status`
- `verification_outcome.summary`
- `baton.verification_status`

Especially for tool/worker routes.

### Rule

> **Route selection and truth status are separate decisions.**

---

## 12. Session-aware routing note

If a request contains continuity signals such as:

- continue
- resume
- from yesterday
- previous read
- same repo/thread/ticker

the host should prefer reusing an existing `session_id` rather than creating a new one.

### Rule

> **Continuity signals should bias toward session reuse, not session churn.**

This pairs naturally with the current session round-trip behavior.

---

## 13. Minimal host route metadata

When the host routes into the kernel, these metadata fields are enough for v0.1:

- `channel`
- `thread_id`
- `route`
- `user_scope`
- `host_runtime`

Do not overstuff host metadata.

The kernel already has a compact session contract.

---

## 14. Anti-patterns

Avoid these.

### Anti-pattern A — route everything through the kernel

This wastes structure and compute.

### Anti-pattern B — route nothing through the kernel

This discards the value of monitor/gate/verification/baton continuity.

### Anti-pattern C — host persists every internal field

This turns continuity into a kernel dump.

### Anti-pattern D — separate “Tracey route” at host level

Tracey is kernel-side, not a host route target.

### Anti-pattern E — treat `status = ok` as “truth passed”

This flattens verification.

### Anti-pattern F — create a new session for every request

This destroys round-trip continuity.

---

## 15. Recommended host defaults for v0.1

### Default direct host chat

for:

- low-risk casual requests
- no continuity need
- no execution need

### Default kernel direct reasoning

for:

- structured build/runtime/spec conversations
- continuity-aware analysis
- Tracey-relevant build/home posture inside kernel

### Default kernel + worker/tool path

for:

- finance/tool-bound tasks
- execution-dependent workflows
- verification-sensitive requests

### Default clarify/reject

for:

- malformed requests
- missing critical context
- unsupported route shapes

---

## 16. One-line summary

> **OpenClaw host routing should stay selective: send only continuity-aware, verification-sensitive, or tool-dependent requests into the state-agent kernel; keep casual low-structure requests in direct host chat; persist only compact continuity; and never treat Tracey or kernel internals as separate host-level route targets.**

