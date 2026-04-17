# state-memory-agent-main

An active canary runtime repo for bounded agent execution, plurality-aware coordination, and continuity-sensitive synthesis.
<<<<<<< HEAD

=======
git add docs/CANONICAL_STATUS.md
git commit -m "docs: add canonical repo role lock and current build status"
git push origin main
>>>>>>> d7497ef (docs: restore canonical README spine for active repo)
## Core thesis

This repository is not building a generic multi-agent chatbot.

It is building a runtime where:

- **main brain** remains synthesis authority
- **workers/tools** provide bounded capability, never final judgment
- **governance** controls whether the system may proceed
- **family runtime layers** preserve distinct child perspectives without collapsing them into one voice
- **disagreement** can remain open rather than being flattened into fake consensus
- **reconciliation** distinguishes operational alignment from epistemic convergence
- **observability** makes the runtime inspectable
- **shell/transport/server layers** expose the system to the outside without corrupting the core boundary

---

## Repo role

`state-memory-agent-main` is the **active canary integration repo**.

Use this repo as the place where the current family-runtime spine is being assembled, tested, and normalized.

Compared with `state-memory-agent`, this repo is the one carrying the newer canary layers and integration passes. The older repo still matters as lineage and reference, but this repo should be treated as the current build surface unless explicitly stated otherwise.

---

## Current status

Recommended current label:

> **Internal Alpha — active canary runtime spine with bounded authority**

The repo now contains:

- shared state bus canary
- disagreement object and locality split
- effort allocator canary
- monitor + mirror canary
- router decision canary
- verification loop canary
- execution gate canary
- context view canary
- mode inference canary
- live state register canary
- delta log canary
- compression layer canary
- reactivation layer canary
- family turn pipeline canary
- turn handoff canary

This means the repo is no longer only spec-heavy. It now has a thin operational spine capable of dry-run family-layer composition while preserving bounded authority, honest verification posture, and open disagreement.

---

## What is currently true

At the current canary stage, the runtime can already model:

- **current reality framing** via context view
- **present-turn mode inference**
- **compact live operational posture**
- **direction-of-motion logging** via delta log
- **shape-preserving continuity compression**
- **cue-based minimum-shape reactivation**
- **pre-action monitoring and mirror summarization**
- **effort routing and temporary lead selection**
- **verification honesty without fake completion**
- **permission gating before any execution-like posture**
- **cross-turn baton handoff without transcript replay**

What it still does **not** do is full production orchestration, persistence-final continuity, unrestricted execution, or public-runtime hardening.

---

## Quickstart

### 1. Activate your virtual environment

PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

bash:
```bash
source .venv/bin/activate
```

### 2. Install dependencies

PowerShell:
```powershell
./scripts/bootstrap_dev_env.ps1
```

bash:
```bash
bash ./scripts/bootstrap_dev_env.sh
```

### 3. Run tests

PowerShell:
```powershell
./scripts/test_local.ps1
```

bash:
```bash
bash ./scripts/test_local.sh
```

### 4. Run the local app surface

PowerShell:
```powershell
./scripts/run_app_local.ps1
```

bash:
```bash
bash ./scripts/run_app_local.sh
```

Then check:

- `GET /health`
- `GET /ready`
- `POST /webhooks/telegram`

---

## High-level architecture

### Authority
- main brain = synthesis authority
- workers / children / tools = bounded influence only

### Runtime layers
- context view
- mode inference
- live state register
- monitor / mirror
- effort allocator
- router decision
- execution gate
- verification loop
- delta log
- compression
- reactivation
- turn handoff

### Family coordination layers
- shared bus
- disagreement register / carried status
- plurality-preserving router posture
- verification-honest turn pipeline

### External layers
- shell contract
- operator console
- transport abstraction
- webhook boundary
- FastAPI app surface
- process/deployment skeleton

---

## Important docs

- `docs/ARCHITECTURE_CURRENT.md`
- `docs/LAW_INDEX.md`
- `docs/project-state-map.md`
- `docs/architecture-overview.md`
- `docs/release-roadmap.md`
- `docs/component-maturity.md`
- `docs/next-build-order.md`
- `docs/BOOTSTRAP_LOCAL.md`
- `docs/OPERATOR_RUNBOOK.md`

If `state-memory-agent` remains available in parallel, treat it as lineage/reference unless a document explicitly says it is still the canonical source for a specific subsystem.

---

## Repo reading order

For a new builder/operator, the fastest order is:

1. `README.md`
2. `docs/ARCHITECTURE_CURRENT.md`
3. `docs/LAW_INDEX.md`
4. `docs/component-maturity.md`
5. `docs/next-build-order.md`
6. current family-layer canary files under `src/family/`
7. turn-pipeline / handoff integration files

---

## What this project is not yet

Not yet:

- production-hardened
- secret-managed
- persistence-finalized
- deployment-platform-specific
- ready for uncontrolled public traffic
- a full orchestration runtime
- a final memory retrieval system
- a trusted execution platform

This repo should still be treated as a serious **internal alpha canary scaffold**.

---

## Development principle

Do not optimize for the illusion of intelligence.

Optimize for:

- bounded authority
- explicit law
- inspectable state
- preserved disagreement
- honest verification
- permission before execution
- compact continuity without transcript replay
- maintainable runtime shape

---

## Immediate next priority

Before adding broad new features, prefer:

- canonicalization
- pipeline-order normalization
- handoff normalization
- documentation recovery
- integration tightening

The current risk is no longer only missing modules.
It is also **drift between code growth and canonical repo shape**.
