# Architecture Overview

This repository should be read as a **layered runtime scaffold**, not as a generic equal-voice agent swarm.

Core principle:

> **main brain authority**
> + **bounded workers**
> + **governance discipline**
> + **family floor**
> + **child runtime layers**
> + **plurality without fake consensus**
> + **observability**

The system is organized so different components have different rights, responsibilities, and authority levels.

---

## Current canonical runtime docs

Use these first:

- `ARCHITECTURE_CURRENT.md` — live runtime center and authority map
- `LAW_INDEX_operationalized.md` — operational law layer
- `project-state-map.md` — what is currently integrated and how the stack is shaped
- `monitor_position_canonical_v0.1.md` — canonical monitor/governance position
- `runtime-minimum-v0.md` — minimum acceptable runtime before wider exposure

---

## Operator / build docs

Use these when running, testing, or hardening the local system:

- `OPERATOR_RUNBOOK.md`
- `security-hardening-checklist-v0.md`
- `BOOTSTRAP_LOCAL.md`
- `LOCAL_SMOKE_TEST_CHECKLIST.md`
- `LOCAL_TROUBLESHOOTING.md`
- `OPENCLAW_LOCAL_INTEGRATION.md`

---

## Current architecture thesis

The active architecture is built around five non-negotiable ideas:

1. **Axis before capability**  
   Capability is allowed to expand only under a stable runtime shape.

2. **Main-brain synthesis authority**  
   Workers, child passes, and tools provide bounded evidence or interpretations.  
   They do not become final authority.

3. **Governance as intermediate control**  
   Monitor, mirror, and related control passes sit between raw generation and final commit behavior.

4. **State-memory / continuity spine**  
   The system is designed to preserve posture, not just transcript fragments.

5. **Plurality without fake collapse**  
   Disagreement is allowed to remain real, and action lead does not equal truth resolution.

---

## Historical / lineage docs

These remain valuable, but they are not the live runtime center:

- `full_spec.md`
- `docs/lineage/v3-merged-operating-model.md`
- `v1_frozen_architecture.md`

Read them for lineage, origin logic, and architecture history — not as the current runtime contract.

---

## Practical reading order

### If you are editing architecture
1. `ARCHITECTURE_CURRENT.md`
2. `LAW_INDEX_operationalized.md`
3. `project-state-map.md`
4. `monitor_position_canonical_v0.1.md`

### If you are running locally
1. `BOOTSTRAP_LOCAL.md`
2. `LOCAL_SMOKE_TEST_CHECKLIST.md`
3. `OPERATOR_RUNBOOK.md`
4. `LOCAL_TROUBLESHOOTING.md`

### If you are reviewing lineage
1. `full_spec.md`
2. `docs/lineage/v3-merged-operating-model.md`
3. `v1_frozen_architecture.md`

---

## Current boundary

The current repository is best understood as:

> **an internal alpha runtime scaffold**

It is already more than a loose prototype.
It is not yet a public-ready product shell.
