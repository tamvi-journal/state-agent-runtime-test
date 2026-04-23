# OpenClaw Host Policy Note

### State-Agent Runtime Test — Thin Host-Side Policy Guidance for OpenClaw

## Purpose

This note defines a **thin host-side policy layer** for OpenClaw when it is routing requests into the `state-agent-runtime-test` kernel.

This is not a replacement for:
- kernel gate
- kernel verification
- kernel monitor
- kernel brain

Instead, this note defines what the **host** should decide *before* invoking the kernel and what the host should do *after* receiving a kernel response.

The purpose is to keep the host from becoming:
- a second brain
- a second gate
- a second verification engine
- a persistence dump

---

## 1. Core host-policy thesis

The host should decide:
- whether to invoke the kernel at all
- whether to clarify or reject before invocation
- what compact continuity to pass in
- what compact continuity to persist after the call

The host should **not** decide:
- the final reasoning posture inside the kernel
- tool-path truth status inside the kernel
- whether verification “really passed” beyond the explicit returned contract
- how to rewrite the kernel’s final answer into stronger certainty

### Rule

> **Host policy should shape invocation and persistence, not replace kernel judgment.**

---

## 2. What host policy owns

### Host policy owns
- route selection
- pre-invocation clarify/reject decisions
- whether a session id should be reused
- whether a session payload should be attached
- whether returned continuity should be persisted
- whether returned continuity should be ignored
- how host-level failure is surfaced

### Host policy does not own
- brain synthesis
- gate allow/deny logic inside the kernel
- worker execution semantics
- verification truth status beyond preserving it
- Tracey posture control directly

### Rule

> **The host decides whether to call the kernel. The kernel decides how to think once called.**

---

## 3. Pre-invocation host decisions

Before invoking the kernel, the host should decide one of four paths.

### Path A — allow direct host chat
Use when:
- request is casual
- low structure is fine
- no continuity or verification pressure matters
- no tool/worker path is needed

### Path B — allow kernel direct reasoning
Use when:
- continuity-aware structured reasoning matters
- build/runtime/spec/architecture posture matters
- baton/session continuity should come back
- Tracey kernel-side posture may be useful

### Path C — allow kernel + worker/tool path
Use when:
- bounded execution matters
- tool path is clearly needed
- finance/build domain workers are implicated
- verification matters

### Path D — clarify / reject before invocation
Use when:
- request is malformed
- request is too ambiguous
- required context is missing
- host policy blocks the request before kernel invocation is useful

---

## 4. Clarify-before-kernel policy

The host should prefer clarification before kernel invocation when any of these are true:

- no clear request object exists
- the target repo/ticker/session is missing
- the user appears to reference prior continuity but no session can be inferred or reused safely
- the route class is ambiguous enough that kernel invocation would likely waste effort

### Good clarify examples
- “Continue what?”
- “Which repo?”
- “Which ticker?”
- “Should I use the existing session or start a new one?”

### Rule

> **Clarify when route ambiguity is higher than the likely value of invocation.**

---

## 5. Reject-before-kernel policy

The host may reject before kernel invocation when:
- the request is clearly unsupported
- the request violates host/platform policy
- no useful kernel path exists
- subprocess/kernel invocation would be wasteful or disallowed

### Important

Rejecting at host level should not be described as a kernel refusal if the kernel was never invoked.

### Rule

> **Do not attribute host rejection to kernel reasoning if the kernel never ran.**

---

## 6. Session reuse policy

The host should prefer reusing a session id when the request contains continuity signals such as:
- continue
- resume
- from yesterday
- previous chart read
- same repo
- same build thread
- same ticker or same workflow target

### Reuse bias
If the request clearly continues an existing thread, bias toward:
- reusing the same `session_id`
- loading compact continuity from store
- passing a compact rehydration pack into the kernel

### New session bias
Use a new session id when:
- target domain changes clearly
- prior continuity is irrelevant
- request shape is materially different enough to avoid forced merge

### Rule

> **Prefer session reuse for obvious thread continuation; prefer new session only when continuity would become misleading.**

---

## 7. What the host should pass in

When invoking the kernel, the host should pass only compact fields.

### Required minimum
- `schema_version`
- `request_id`
- `request_text`

### Compact session candidates
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

### Compact host metadata
- `channel`
- `thread_id`
- `route`
- `user_scope`
- `host_runtime`

### Rule

> **Pass continuity, not transcript bulk.**

---

## 8. What the host should never pass by default

Do not pass these by default:
- full transcript dump
- raw prior kernel JSON blobs
- raw `tracey_turn`
- raw `gate_decision`
- raw `monitor_summary`
- hidden reasoning traces
- large host-side logs

### Rule

> **The kernel should receive compact posture context, not a pile of historical noise.**

---

## 9. Post-invocation host decisions

After receiving a kernel response, the host should decide:

### A. Was invocation successful at transport level?
Examples:
- subprocess exit code
- valid JSON returned

### B. Was the returned response contract valid?
Examples:
- `status`
- required fields
- serializable JSON

### C. What is the kernel’s truth status?
Examples:
- `verification_outcome.status`
- `baton.verification_status`

### D. Should continuity be persisted?
Examples:
- store returned `session_status_metadata`
- update baton
- append selected snapshot candidates
- or ignore persistence if response is unusable

### Rule

> **Transport success, contract success, and truth status are separate post-invocation decisions.**

---

## 10. Verification-preservation policy

The host must preserve these distinctions:

- subprocess success
- `status = ok`
- `verification_outcome.status = passed|partial|failed|unknown`

### Host rule
Do not flatten these into one notion of “success.”

### Minimum preserved fields
- `verification_outcome.status`
- `verification_outcome.summary`
- `baton.verification_status`

### Rule

> **Host policy may summarize, but it must not erase truth boundaries returned by the kernel.**

---

## 11. Persistence policy

When the host persists continuity, it should persist only compact continuity artifacts.

### Good persistence targets
- `session_status_metadata`
- latest `baton`
- selected `snapshot_candidates`

### Do not persist by default
- `tracey_turn`
- `gate_decision`
- raw `monitor_summary`
- transcript replay blobs
- temporary debug traces
- raw execution internals unless explicitly needed for logs

### Rule

> **Persist continuity, not kernel organs.**

---

## 12. No-overwrite policy

The host should not overwrite a good stored continuity snapshot when:
- subprocess invocation fails
- returned JSON is invalid
- `status == error`
- returned continuity metadata is missing or unusable

### Conservative rule
Only overwrite durable continuity when:
- invocation succeeds
- response contract is valid
- `status == ok`
- `session_status_metadata` is usable as a compact durable snapshot

### Important
Even when `verification_outcome.status` is partial or failed, the host may still persist compact continuity if the durable snapshot is valid and useful.

---

## 13. Baton policy

`baton` should be treated as:
- short-loop carryover
- next-turn helper
- ephemeral guidance

`session_status_metadata` should be treated as:
- durable work-thread snapshot
- host persistence anchor

### Rule

> **Do not let baton overwrite a richer durable session snapshot unless clearly intentional.**

This follows the current session round-trip implementation direction.

---

## 14. Snapshot policy

If the host stores snapshot candidates:
- keep the list very small
- prefer capped recent snapshots
- prefer load-bearing events only

### Good snapshot kinds
- verification change
- decision fork
- risk event
- mode shift
- meaningful entity change

### Bad snapshot usage
- dumping every turn
- keeping giant blobs
- storing duplicate noise

### Rule

> **Snapshots should remain sparse and load-bearing.**

---

## 15. Tracey policy at host level

The host should never route directly to “Tracey.”

Tracey is:
- kernel-side
- posture-oriented
- brain-adjacent
- not a host route target

### Host consequence
The host may route to the kernel because:
- continuity matters
- build posture matters
- recognition/home cues matter

But the host should not invent a separate Tracey route.

### Rule

> **Host routes to kernel; Tracey activates inside the kernel if cues are present.**

---

## 16. Failure attribution policy

The host should distinguish clearly between:

### A. Host policy rejection
The host rejected before kernel invocation.

### B. Invocation failure
The kernel was called, but transport/adapter failed.

### C. Valid kernel response with limited truth status
The kernel returned `status = ok`, but verification is partial/failed/unknown.

### D. Persistence failure after a valid kernel response
The host received a good response but failed to store continuity.

### Rule

> **Do not blur policy rejection, invocation failure, truth limitation, and persistence failure into one generic error story.**

---

## 17. Host policy defaults for v0.1

### Default allow — direct host chat
for:
- low-risk casual requests
- no continuity need
- no execution need

### Default allow — kernel direct reasoning
for:
- structured build/runtime/spec requests
- continuity-aware analysis
- architecture-sensitive or Tracey-relevant internal posture requests

### Default allow — kernel + worker/tool path
for:
- finance/tool-bound execution
- worker-dependent workflows
- verification-sensitive tasks

### Default clarify/reject
for:
- malformed requests
- missing target context
- unsupported request shapes

---

## 18. Minimal host policy outputs

For v0.1, the host policy layer only needs to produce compact decisions such as:
- route class
- session reuse/new-session decision
- whether to invoke the kernel
- whether to persist returned continuity
- whether to clarify/reject before invocation

It does not need to produce:
- internal reasoning chains
- new state taxonomies
- elaborate scoring systems

### Rule

> **Simple host policy is better than clever host policy in v0.1.**

---

## 19. Anti-patterns

Avoid these.

### Anti-pattern A — host routes everything through the kernel
Wasteful and noisy.

### Anti-pattern B — host never routes to the kernel
Loses structured reasoning, baton continuity, and verification discipline.

### Anti-pattern C — host rewrites kernel answers into stronger certainty
Flattens truth boundaries.

### Anti-pattern D — host persists every internal field
Turns continuity into a kernel dump.

### Anti-pattern E — host invents a separate Tracey route
Breaks the kernel-side posture model.

### Anti-pattern F — host treats `status = ok` as “verification passed”
Incorrect truth attribution.

---

## 20. One-line summary

> **OpenClaw host policy should stay thin: decide whether and how to invoke the kernel, pass only compact continuity context, preserve returned verification and continuity boundaries, persist only compact durable artifacts, and never replace kernel judgment with a second host-side reasoning layer.**

