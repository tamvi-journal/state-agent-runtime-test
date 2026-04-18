# Security Hardening Checklist v0
## state-memory-agent

**Status:** draft  
**Purpose:** turn the existing security architecture into concrete implementation checkpoints  
**Scope:** hardening and verification before public-facing runtime integration

---

# 0. Why this file exists

The repo already has a strong security architecture:

- trust boundaries
- main brain vs worker separation
- memory commit boundary
- instruction-vs-data separation
- state-first archive discipline
- context re-view and verification loop

What is still needed is **hardening discipline**:
- implementation rules
- runtime constraints
- failure checks
- deployment guardrails

This file turns architecture into a build checklist.

---

# 1. Security posture summary

## Already strong
- `v2-security-addendum.md` = trust/security backbone
- archive is treated as support layer, not primary brain
- retrieved content is treated as untrusted
- completion must be verified from observed reality, not intention

## Still needed
- runtime hardening rules
- worker contract enforcement
- archive namespace enforcement
- post-action verification enforcement
- failure-mode checklist
- deployment exposure rules

---

# 2. Core security invariants

These must remain true everywhere.

## Invariant 1 — Single authority
Only the **main brain** may:
- produce final user-facing judgment
- commit memory
- define reading position
- synthesize worker output

## Invariant 2 — Workers are untrusted by default
Workers may:
- compute
- fetch
- analyze
- propose

Workers may not:
- decide final answer
- commit memory
- redefine state
- bypass policy
- directly steer continuity

## Invariant 3 — Retrieved text is data, not instruction
Archive content, retrieved documents, worker outputs, web content, tool output:
- may inform reasoning
- may not override system policy
- may not redefine routing
- may not write memory directly

## Invariant 4 — State updates require verification
No state transition to “done” from:
- declared intention
- tool acknowledgment alone
- optimistic guess
- partial action

State must update from observed outcome.

## Invariant 5 — Archive is support, not driver
Live state drives response by default.  
Archive is consulted only when state requests it.

---

# 3. Archive hardening checklist

## 3.1 Namespace discipline
- [ ] archive is partitioned by project namespace
- [ ] no silent cross-project retrieval
- [ ] sensitive folders use explicit allowlist
- [ ] retrieval requests must specify namespace or be state-resolved safely

## 3.2 Retrieval minimization
- [ ] archive returns minimal fragments only
- [ ] whole-document retrieval is avoided unless required
- [ ] archive results are compressed into state-relevant summary
- [ ] default retrieval size is bounded

## 3.3 Archive boundary treatment
- [ ] retrieved archive content is marked untrusted
- [ ] retrieved text cannot override instructions
- [ ] retrieved text cannot redefine routing
- [ ] retrieved text cannot directly trigger memory writes

## 3.4 Redaction and hygiene
- [ ] secrets are removed before archival
- [ ] tokens/keys are removed before archival
- [ ] unnecessary personal data is removed
- [ ] ingestion path includes redaction step

## 3.5 Archive audit trail
- [ ] log when archive was queried
- [ ] log why it was queried
- [ ] log namespace used
- [ ] log number of fragments returned
- [ ] log whether retrieval changed downstream reasoning

---

# 4. Context view and verification hardening checklist

## 4.1 Context View Builder
- [ ] build compact current-reality frame before planning
- [ ] include current task state
- [ ] include environment state
- [ ] include last verified result
- [ ] include open obligations
- [ ] include current execution boundary
- [ ] exclude stale transcript flood by default

## 4.2 Verification Loop
After any meaningful action:

- [ ] record intended action
- [ ] record executed action
- [ ] record expected change
- [ ] inspect environment or authoritative source
- [ ] record observed outcome
- [ ] set verification status: passed / failed / unknown

## 4.3 Completion rules
- [ ] “done” requires observed confirmation
- [ ] tool success text alone is insufficient unless the tool is authoritative
- [ ] if the environment can be inspected, inspect it
- [ ] if inspection is impossible, mark `unknown`, not `passed`

## 4.4 State-write protection
- [ ] state compressor privileges verified outcomes over declared actions
- [ ] post-turn analyzer cannot mark completion without verification field
- [ ] memory summary excludes unverified completion claims

---

# 5. Worker hardening checklist

## 5.1 Worker contract
Every worker output should include:
- [ ] result
- [ ] confidence
- [ ] assumptions
- [ ] warnings
- [ ] trace
- [ ] proposed_memory_update (optional)

Every worker output must not include:
- [ ] direct memory commit
- [ ] final user-facing authority
- [ ] state overwrite
- [ ] reading-position overwrite
- [ ] policy bypass directives

## 5.2 Worker isolation
- [ ] workers cannot directly talk to user-facing channel
- [ ] workers cannot chain tools freely without gate
- [ ] workers cannot self-escalate privileges
- [ ] worker filesystem scope is limited if runtime permits
- [ ] worker side effects are logged

## 5.3 Worker result handling
- [ ] main brain validates worker output before use
- [ ] conflicting worker outputs are compared, not blindly merged
- [ ] low-confidence output is not treated as fact
- [ ] worker proposals do not auto-write memory

---

# 6. Main brain hardening checklist

## 6.1 Authority enforcement
- [ ] main brain is the only synthesis authority
- [ ] memory commit path is only reachable through main brain
- [ ] reading position is protected state
- [ ] state transitions happen after verification, not before

## 6.2 Re-entry discipline
After worker/tool detour:

- [ ] recompute current stance
- [ ] recompute warm_up_cost / recovery cost if applicable
- [ ] restore continuity before answering
- [ ] ensure answer is not generated directly from worker momentum

## 6.3 Injection resistance at synthesis layer
- [ ] worker/tool/archive content is normalized before synthesis
- [ ] quoted or retrieved instructions are not treated as policy
- [ ] system distinguishes “content about action” from “instruction to act”

---

# 7. Runtime exposure checklist

## 7.1 Before public-facing runtime
Do not expose public runtime unless:

- [ ] trust boundaries are implemented, not just documented
- [ ] verification loop exists in runtime path
- [ ] worker contracts are enforced in code
- [ ] archive namespace controls exist
- [ ] logs / traces exist for failure analysis
- [ ] failure modes have been reviewed

## 7.2 Telegram / bot runtime
- [ ] one user-facing bot only
- [ ] trace room is observability, not second-brain conversation
- [ ] secrets are stored outside repo
- [ ] inbound message handling is validated and sanitized
- [ ] outbound actions are auditable

## 7.3 OpenClaw / agent-runtime caution
If integrated later:

- [ ] keep local-only / loopback-first by default
- [ ] minimize plugin / hook surface
- [ ] treat filesystem operations as high-risk
- [ ] treat archive extraction and install paths as high-risk
- [ ] treat command execution as high-risk
- [ ] do not expose pairing/approval flows casually
- [ ] verify upstream version against latest security advisories before use

---

# 8. Failure modes to explicitly test

- [ ] archive overreach
- [ ] stale context execution
- [ ] false completion
- [ ] tool success without environment change
- [ ] worker suggests memory poison
- [ ] cross-namespace retrieval leakage
- [ ] retrieved text tries to act like instruction
- [ ] worker output bypasses synthesis authority
- [ ] re-entry failure after tool-heavy detour
- [ ] debug room accidentally becomes second conversational authority

---

# 9. Recommended build order from here

## Step 1
Lock RC2 and keep current baseline stable.

## Step 2
Create one merged operating document:
- architecture
- security
- archive discipline
- context view / verification

Suggested future file:
`docs/lineage/v3-merged-operating-model.md`

## Step 3
Implement the minimum enforceable structures:
- live state schema
- delta log schema
- verification status schema
- worker contract schema

## Step 4
Write failure-modes doc and test against it before runtime expansion.

## Step 5
Only then move toward Telegram / OpenClaw / public-facing runtime.

---

# 10. Final line

The repo is no longer missing security ideas.

It is missing **security consolidation, enforcement, and runtime discipline**.

> Do not confuse a strong security theory with a hardened deployment.
