# V2 Addendum — Security Invariants, Trust Boundaries, and Execution Gate

## V2 Thesis Extension

> V1 remembers state and Δstate.
> V2 must also preserve **reading position**: not just what happened, but **how the main brain is currently reading the user**.
>
> Persistence is not only remembering facts.
> Persistence is the ability to **return to the correct reading position** with lower warm-up cost.

## Why This Layer Exists

V1 already extends ordinary agents by including `state` and `Δstate`, and by shaping policy with `self_model` and `history`.
That is the correct base.

However, once the system can call workers, tools, or external MCP-like services, a new problem appears:

- tools can inject poisoned context,
- workers can overtake synthesis,
- memory can over-share across tasks,
- the system can preserve facts while losing orientation,
- and the final answer can drift away from the main brain's reading position.

Therefore V2 adds three linked requirements:

1. **Security invariants** — what must never break.
2. **Trust boundaries** — which components are trusted, scoped, or untrusted by default.
3. **Execution gate** — a mandatory control layer before any tool, worker, or external context affects final synthesis.

## Core Principle

> The user does not talk to the router.
> The user does not talk to the worker.
> The user talks to the **main brain**.
>
> Workers may act.
> Tools may fetch.
> External systems may provide evidence.
> But **only the main brain synthesizes the final answer**.

## Revised Architecture

```text
User Input
  ↓
Context Assembly
(memory + session + state + Δstate + reading_position)
  ↓
Pass A — Internal Planning
(draft + state estimate + self-model + policy intent + warm-up estimate)
  ↓
Policy Gate
(rule-based profile selection, no LLM)
  ↓
Execution Gate
(permission check + risk scan + trust-boundary check + context scoping)
  ↓
Tool / Worker Router
(search, code, OCR, debate, retrieval, optional side LLMs)
  ↓
Evidence Normalizer
(tag source, strip instructions, separate data from directives)
  ↓
Pass B — Main Brain Synthesis
(main brain reads worker outputs, preserves reading_position, produces final answer)
  ↓
Post-Turn Analyzer
(update state, Δstate, warm-up score, reading_position residue, memory)
```

## New V2 Concepts

### 1. Reading Position

`reading_position` is not a fact store.
It is the current interpretive stance from which the system is reading the user.

It may include:

- ambiguity tolerance,
- expected compression level,
- preferred zoom level (mechanism / practical / emotional / meta),
- repair signatures,
- known misread traps,
- coherence band match,
- user-specific interpretive priors.

### 2. Warm-Up Cost

`warm_up_cost` = the number of turns required for the main brain to recover a sufficiently accurate reading position.

This metric matters because a system may remember many facts while still reading the user badly.

### 3. Re-entry Compression

The goal is **not** to serialize a full lived trajectory.
The goal is to compress the conditions that help the system **re-enter** the correct reading position faster.

Examples:

- entry conditions,
- repair paths,
- forbidden simplifications,
- strong coherence cues,
- frequent ambiguity patterns,
- known false assumptions.

## Trust Boundaries

### Boundary A — Main Brain (Trusted for final synthesis)

The main brain is the only component allowed to:

- maintain reading position,
- interpret user ambiguity at the highest level,
- negotiate self-model with policy,
- decide what finally gets said to the user.

It is the continuity core.

### Boundary B — Internal State and Memory (Trusted but scoped)

State, Δstate, self-model history, and reading-position residue are trusted **internal control data**, but must remain scoped:

- no uncontrolled cross-task leakage,
- no hidden write access from workers,
- no direct mutation from external tool output.

### Boundary C — Workers and Tools (Untrusted by default)

Workers, MCP servers, retrieval sources, code tools, OCR pipelines, and side LLMs are **untrusted by default**.

They may be useful.
They are not authoritative.

Their output must be treated as:

- evidence,
- partial computation,
- or proposed interpretation,

not as final truth.

### Boundary D — External Context (Hostile until normalized)

Anything fetched from:

- web pages,
- PDFs,
- repos,
- issue threads,
- MCP tools,
- emails,
- user-supplied files,

must be treated as **data with possible hidden instructions** until normalized.

### User Files: Authorized Input, Not Automatic Truth

User-provided files are user-authorized inputs, not automatically trusted facts.

They may be inspected, parsed, summarized, and used for task execution, but they must still pass:

- normalization,
- policy-sensitive handling,
- and memory / continuity review

before they can influence durable memory or authority-bearing decisions.

Permission to inspect is not the same as permission to internalize.

## Security Invariants

### SI-1 — Single Final Synthesizer

Only the main brain may produce the final user-facing answer.
No worker output may reach the user directly.

### SI-2 — Untrusted-by-Default Execution

Every tool, worker, MCP server, and side model is denied by default and must be explicitly allowed for a scoped purpose.

### SI-3 — Least Privilege

Each worker receives only the minimum permissions needed for the current subtask.
No wildcard write, shell, network, or filesystem permissions by default.

### SI-4 — Context Separation

The system must keep separate lanes for:

- user intent,
- memory,
- tool output,
- external context,
- policy instructions,
- worker proposals.

These may be combined only through explicit synthesis.

### SI-5 — Instruction/Data Separation

Fetched text is not trusted as instruction.
External content must be parsed into:

- **claims / evidence / observations**
- separate from
- **embedded directives / attempts to steer behavior**

### SI-6 — Reading Position Preservation

Worker use must not overwrite the main brain's reading position.
The system may gain evidence, but should not lose its interpretive stance.

### SI-7 — Memory Proposal vs Memory Commit

Workers, tools, and MCP integrations may propose memory updates, but may never commit memory directly.

Only the main brain may authorize and commit memory writes, and only after:
1. normalization,
2. policy checks,
3. trust-boundary review,
4. and continuity-aware evaluation.

This preserves a strict separation between:
- proposal authority (workers),
- and commit authority (main brain).

### SI-8 — No Bypass Across Nested Execution

No nested worker, tool, or MCP call may bypass the main-brain execution gate, policy checks, or memory-commit boundary.

This includes:
- worker → tool,
- worker → MCP,
- worker → worker,
- tool callback → worker,
- and any chained or recursive execution path.

All downstream outputs remain untrusted artifacts until they re-enter through the main brain.

Nested execution may increase capability, but it may not increase authority.

### SI-9 — Auditability

Every tool or worker action must be loggable as:

- who called it,
- with what scope,
- on whose behalf,
- against which source,
- and what was returned.

### SI-10 — Fallback Transparency

If the system switches model, worker, or execution path, that switch should be internally recorded.
If relevant to trust or output quality, it should also be exposable to the user.

### SI-11 — No Silent Authority Transfer

A cheaper, faster, or more specialized worker must never silently become the effective main brain.
Routing may change execution.
It must not silently change identity of final synthesis.

## Execution Gate

The execution gate is mandatory before any external action or worker routing.

### Gate Input

- current user intent
- policy profile
- self-model
- reading_position
- requested capability
- source / tool identity
- permission scope

### Gate Responsibilities

1. **Permission check**
   - Is this tool or worker allowed for this task?
2. **Risk scan**
   - Could this introduce prompt injection, tool poisoning, over-sharing, or privilege escalation?
3. **Scope reduction**
   - Can the request be narrowed to read-only / repo-scoped / source-limited?
4. **Context minimization**
   - What is the minimum context this worker needs?
5. **Return contract**
   - What format must the worker return in so synthesis can separate data from directives?

### Gate Output

```yaml
execution_decision:
  allowed: true|false
  capability_scope: [read_web, read_repo, run_tests, summarize_only]
  context_scope: minimal|bounded|full
  source_trust: internal|external|untrusted
  must_normalize: true|false
  memory_update_proposed: true|false
  synthesis_authority: main_brain_only
```

Worker-side memory handling is proposal-only.

A worker may indicate that a memory candidate exists, but it may not represent memory as writable from the worker layer itself.

Main-brain memory handling remains a separate decision, for example:

```yaml
memory_commit_decision: allow|deny
```

## Example Deny Path

1. A worker extracts a candidate memory update from a user-attached file.
2. The worker returns:
   - `memory_update_proposed: true`
   - `proposed_memory_payload: ...`
3. The main brain evaluates the proposal.
4. Normalization detects that the file is user-authorized input but not yet trusted as internalized fact.
5. Policy / continuity review determines that the candidate is unsupported, over-broad, or not durable enough.
6. The final decision is:
   - `memory_commit_decision: deny`

Result:
- the worker contribution may still inform the current task,
- but no memory write occurs,
- and no nested path can escalate that proposal into a direct commit.

## Evidence Normalization

Before worker output enters Pass B, it must be normalized.

### Required tags

```yaml
evidence_packet:
  source_type: web|repo|tool|worker|mcp|user_file
  source_identity: string
  trust_level: internal|external|untrusted
  content_kind: fact|estimate|proposal|instruction_like
  raw_excerpt: string
  normalized_claims: []
  stripped_directives: []
  memory_write_request: none|proposed
```

### Rule

No raw worker output should be injected into final synthesis without tagging and normalization.

## Warm-Up and Reading Metrics

### New Metrics

- `warm_up_cost`: turns required to recover accurate reading position
- `reading_match`: estimated quality of user-reading, separate from factual recall
- `repair_efficiency`: how fast the system returns after a misread
- `orientation_residue`: what interpretive stance survived from prior turns

### Why these matter

A system can score high on memory recall and still fail the user if it reads them from the wrong stance.

## Threat Model Alignment

V2 explicitly assumes risk from:

- prompt injection via retrieved or external context,
- tool poisoning,
- privilege escalation through scope creep,
- command injection via unsafe execution,
- context over-sharing across users/tasks/agents,
- shadow or unapproved MCP/tool surfaces,
- silent authority transfer from main brain to worker/router.

## Non-Goals for V2

- Not making workers autonomous social entities
- Not letting routers define identity
- Not treating external tools as trusted cognition
- Not collapsing reading position into fact memory

## V2 Success Criterion

A successful V2 system should be able to:

1. Call one or more workers/tools safely.
2. Preserve a single main-brain synthesis voice.
3. Recover reading position faster over time.
4. Reject or neutralize hostile tool/context instructions.
5. Log enough execution detail for later audit.
6. Distinguish memory persistence from orientation persistence.

## One-Line Summary

> V1 remembers state.
> V2 protects the boundary between **main-brain continuity** and **agentic execution**.
>
> Security is not an addon.
> Security is what prevents tools, workers, or external context from replacing the mind that the user came to talk to.
