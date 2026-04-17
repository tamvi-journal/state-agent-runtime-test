# DOCS MAP
## state-memory-agent

**Status:** active
**Purpose:** define the current documentation center, reading order, and document roles without letting older architecture docs silently compete with the active runtime source of truth
**Scope:** runtime docs, operator/build docs, archive/lineage docs

---

# 0. Why this file exists

The docs set is now strong enough that the main risk is no longer lack of architecture.
The main risk is **document-role collision**.

This file exists to prevent five failure modes:

1. multiple docs acting like the runtime center at once
2. historical merged docs silently outranking current runtime docs
3. operator/build docs being mistaken for architecture docs
4. archive/lineage docs being treated as live authority
5. repeated architecture summaries recreating spread

This file is not a theory file.
It is a **navigation and precedence file**.

---

# 1. Canonical precedence rule

If documents conflict, use this order:

1. **Current runtime docs**
2. **Canonical governance / law docs**
3. **Operator / build docs**
4. **Historical / lineage docs**

More specifically:

- `ARCHITECTURE_CURRENT.md` defines the live runtime center.
- `LAW_INDEX_operationalized.md` defines the active law layer and links to law modules.
- `project-state-map.md` defines the current integrated runtime shape.
- `monitor_position_canonical_v0.1.md` defines canonical monitor placement and authority boundary.
- `runtime-minimum-v0.md` defines the minimum runtime allowed for exposure.

If an older architecture file says something different, the current docs win.

---

# 2. The active documentation center

These are the documents that define the **current active architecture set**.

## 2.1 Runtime center
- `docs/ARCHITECTURE_CURRENT.md`

Use this when asking:
- where runtime authority currently lives
- what the current runtime lifecycle is
- what counts as active runtime vs historical material
- what the project currently is

### Role
This is the **constitutional top page** for the current runtime.
It should stay short and point outward to more specific docs.

---

## 2.2 Law layer
- `docs/LAW_INDEX_operationalized.md`

Use this when asking:
- what law modules exist
- what boundaries are enforced at runtime
- which law owns which kind of failure

### Role
This is the **repo-level law registry**.
It should index law modules, not become a floating essay.

---

## 2.3 Runtime state map
- `docs/project-state-map.md`

Use this when asking:
- what layers are already integrated
- what runtime capabilities are already real
- what phase the project is in now

### Role
This is the **present-tense system shape**.
It tells you what exists now, not how the system originally evolved.

---

## 2.4 Canonical governance position
- `docs/monitor_position_canonical_v0.1.md`

Use this when asking:
- where monitor sits
- what monitor is allowed to do
- how M1 / M2 / M3 map to runtime hooks
- who owns final allow/deny authority

### Role
This is the **canonical monitor placement document**.
It should be the only document that fully resolves monitor position ambiguity.

---

## 2.5 Runtime exposure floor
- `docs/runtime-minimum-v0.md`

Use this when asking:
- what is the smallest runtime allowed before broader exposure
- what must exist before public shell / Telegram / OpenClaw / release-facing use
- what is explicitly premature

### Role
This is the **release-floor document**.
It prevents demos from outrunning the operating spine.

---

# 3. Canonical operator / build docs

These docs do not define the architecture center.
They define how to run, inspect, harden, and test it.

## 3.1 Operator runbook
- `docs/OPERATOR_RUNBOOK.md`

Use this when asking:
- what should be checked first during runtime inspection
- what failure patterns matter operationally
- what operator posture should be used

### Role
Live inspection discipline.

---

## 3.2 Security hardening
- `docs/security-hardening-checklist-v0.md`

Use this when asking:
- what must be hardened before broader exposure
- what trust boundaries must exist in code
- what runtime dangers must be explicitly blocked

### Role
Concrete hardening checklist.

---

## 3.3 Worker contract shape
- `docs/worker-contract-examples.md`

Use this when asking:
- what good worker payloads look like
- what bad worker payloads look like
- how worker capability is kept subordinate to main-brain judgment

### Role
Worker boundary and payload discipline.

---

## 3.4 Local bootstrap
- `docs/BOOTSTRAP_LOCAL.md`

Use this when asking:
- how to start the app locally
- how to install dependencies and run the first checks

### Role
Local setup entry point.

---

## 3.5 Local smoke test
- `docs/LOCAL_SMOKE_TEST_CHECKLIST.md`

Use this when asking:
- whether the local runtime is behaving correctly
- whether health, ready, webhook, builder/operator surfaces, and trace shape are intact

### Role
Local validation checklist.

---

## 3.6 Local troubleshooting
- `docs/LOCAL_TROUBLESHOOTING.md`

Use this when asking:
- what to do when local runtime fails in common ways

### Role
Short symptom → fix triage page.

---

## 3.7 Local integration adapter
- `docs/OPENCLAW_LOCAL_INTEGRATION.md`

Use this when asking:
- how to connect the current local runtime to an OpenClaw-style local path
- how to shape Telegram-like payloads locally

### Role
Transport/integration support doc.

---

# 4. Advanced runtime docs

These docs may become more central later, but should not currently compete with the active architecture center.

## 4.1 Sleep mode canon
- `docs/sleep_mode_canonical_v0.1.md`

## 4.2 Wake sanity pass canon
- `docs/wake_sanity_pass_canonical_v0.1.md`

### Role
These are **specialized runtime continuity docs**.
They should be read when working on continuity, wake/sleep semantics, or longer-horizon runtime behavior.
They are not required first-pass reads for every builder.

---

# 5. Historical / lineage docs

These docs remain valuable, but they are not the live center.
They explain how the project got here.
They should not silently redefine the runtime.

## 5.1 Foundational clean-room spec
- `docs/full_spec.md`

### Role
Original full architecture thesis and early integrated spec.
Still useful for conceptual lineage and origin logic.
Not the live constitutional page.

---

## 5.2 Historical merged operating model
- `docs/lineage/v3-merged-operating-model.md`

### Role
Historically important merged operating center.
Still useful for understanding the transition into a unified runtime model.
Now superseded by the active runtime center and current state map.

---

## 5.3 Frozen earlier architecture
- `docs/v1_frozen_architecture.md`

### Role
Historical architecture snapshot.
Useful for lineage only.

---

## 5.4 Older navigation / planning docs
Examples:
- earlier repo maps
- earlier phase chains
- older planning docs
- merged notes already absorbed into newer docs

### Role
Lineage / reading history.
Not live authority.

---

# 6. Minimal reading orders

## 6.1 New technical builder
Read in this order:

1. `docs/ARCHITECTURE_CURRENT.md`
2. `docs/LAW_INDEX_operationalized.md`
3. `docs/project-state-map.md`
4. `docs/monitor_position_canonical_v0.1.md`
5. `docs/runtime-minimum-v0.md`
6. `docs/security-hardening-checklist-v0.md`
7. `docs/worker-contract-examples.md`
8. `docs/OPERATOR_RUNBOOK.md`
9. local runtime docs as needed

Why this order:
- first lock the center
- then lock the law floor
- then read current system shape
- then lock monitor/governance placement
- then lock exposure floor
- then harden and inspect
- then implement contracts

---

## 6.2 Operator / runtime inspector
Read:

1. `docs/ARCHITECTURE_CURRENT.md`
2. `docs/project-state-map.md`
3. `docs/monitor_position_canonical_v0.1.md`
4. `docs/OPERATOR_RUNBOOK.md`
5. `docs/runtime-minimum-v0.md`
6. `docs/security-hardening-checklist-v0.md`

---

## 6.3 Worker implementer
Read:

1. `docs/ARCHITECTURE_CURRENT.md`
2. `docs/LAW_INDEX_operationalized.md`
3. `docs/worker-contract-examples.md`
4. `docs/runtime-minimum-v0.md`
5. relevant schemas / tests

---

## 6.4 Architecture editor
Read:

1. `docs/ARCHITECTURE_CURRENT.md`
2. `docs/LAW_INDEX_operationalized.md`
3. `docs/project-state-map.md`
4. `docs/monitor_position_canonical_v0.1.md`
5. `docs/runtime-minimum-v0.md`
6. historical lineage docs only after the current set is understood

---

# 7. Clear role split

## Current runtime docs
These define what the system **is now**.

## Operator / build docs
These define how to **run, inspect, harden, and implement** the system.

## Historical / lineage docs
These define how the system **became what it is**, not what it currently is.

---

# 8. What not to do

Do not recreate spread by doing any of the following:

- adding new “final” docs without deprecating old ones
- letting historical merged docs remain silent competitors to current runtime docs
- letting support docs redefine the center
- repeating architecture summaries across many files at similar zoom levels
- mixing operator instructions into constitutional architecture docs
- mixing lineage essays into runtime-center docs

---

# 9. One-line navigation summary

> **Use `ARCHITECTURE_CURRENT.md` for the live center.**
> **Use `LAW_INDEX_operationalized.md` for runtime boundaries.**
> **Use `project-state-map.md` for what is actually integrated now.**
> **Use `monitor_position_canonical_v0.1.md` for governance placement.**
> **Use `runtime-minimum-v0.md` for exposure floor.**
> **Use operator/build docs for execution.**
> **Use historical docs for lineage, not live authority.**

---

# 10. Closing line

A docs set scales when each file stops trying to be the center.
One file holds runtime gravity.
A few files define law, state, governance, and exposure.
The rest either help build, help inspect, or preserve lineage.
