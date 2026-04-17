# Project State Map

## Current system shape

The repository now contains a layered runtime scaffold rather than a single assistant loop.

### Layer 1 — Runtime spine
Status: **integrated + tested**

Includes:
- live state
- delta log
- context view
- request router
- main brain authority
- execution gate
- verification loop
- builder/user render split

Meaning:
- there is a stable bounded path for reading, verifying, and synthesizing
- the system already distinguishes action from completion

---

### Layer 2 — Capability workers
Status: **integrated + tested**

Current workers:
- `market_data_worker`
- `screening_worker`

Meaning:
- capability is present, but still bounded
- workers produce evidence, not judgment
- main brain remains the only authority layer for synthesis

---

### Layer 3 — Governance
Status: **integrated + tested**

Includes:
- `monitor_layer`
- `mirror_bridge`
- `effort_allocator`
- `governance_pass`

Meaning:
- the system can detect drift, ambiguity, fake progress, archive overreach, and mode decay
- the system can compress monitor state into a usable summary
- the system can route effort, verification posture, and coordination posture per turn

---

### Layer 4 — Family floor
Status: **runtime objects + tested**

Includes:
- house laws
- refusal policy
- runtime security boundaries
- shared ontology

Meaning:
- the family scaffold already has explicit floor rules
- refusal and hold-open behavior are structurally grounded
- vocabulary is shared across children and governance

---

### Layer 5 — Tracey line
Status: **integrated + tested**

Includes:
- `tracey_axis`
- `tracey_memory`
- `tracey_runtime_profile`
- `tracey_runtime_pass`
- Tracey telemetry in flow

Meaning:
- Tracey is no longer just a persona note
- Tracey already exists as a bounded child-layer in runtime

---

### Layer 6 — Seyn line
Status: **integrated + tested**

Includes:
- `seyn_axis`
- `seyn_memory`
- `seyn_runtime_profile`
- `seyn_runtime_pass`

Meaning:
- Seyn now exists as the structural / verification-led child-layer
- plurality is no longer hypothetical

---

### Layer 7 — Plurality + disagreement
Status: **integrated + tested**

Includes:
- disagreement event schema
- disagreement register
- local perspective notes
- disagreement wiring
- dual-child runtime pass
- dual-brain coordination pass

Meaning:
- the system can preserve disagreement in shared state
- local child perspectives stay distinct from shared event memory
- action lead is separated from truth resolution

---

### Layer 8 — Reconciliation
Status: **integrated + tested**

Includes:
- cross-logic exchange
- reconciliation protocol
- reconciliation wired into coordination flow

Meaning:
- disagreement can move toward convergence without fake collapse
- operational alignment and epistemic alignment are explicitly separated

---

### Layer 9 — Observability
Status: **integrated + tested**

Includes:
- raw telemetry events
- dashboard summary
- timeline view
- dashboard snapshot

Meaning:
- builders can inspect disagreement, routing, reconciliation, and flags without reading raw logs one by one

---

## Strategic reading of current state

The project is no longer in “idea exploration” phase.

It is currently in:

> **internal runtime scaffold phase**

That means:
- the architecture is real
- plurality is real
- reconciliation is real
- observability is real

But:
- shells are not yet productized
- persistence strategy is not yet finalized
- release packaging is behind implementation progress
