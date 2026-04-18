# Release Roadmap

## Current release frame

Recommended label:

> **Internal Alpha — Family Runtime Scaffold**

This is the first point where the project has enough structure to be named as a coherent internal system.

---

## Already present in Internal Alpha

### Runtime core
- bounded runtime spine
- context + verification + synthesis path
- request routing
- builder/user render split

### Capability
- market data worker
- screening worker

### Governance
- monitor
- mirror bridge
- effort allocator
- governance pass

### Family floor
- house laws
- refusal policy
- runtime security boundaries
- shared ontology

### Children
- Tracey runtime core and integration
- Seyn runtime core and integration

### Plurality
- disagreement register
- local perspectives
- dual-child wiring
- dual-brain coordination

### Reconciliation
- cross-logic exchange
- reconciliation protocol
- reconciliation wiring into coordination flow

### Observability
- telemetry
- dashboard summary
- timeline view
- dashboard snapshot

---

## What is still missing before “usable internal alpha”

### A. Runtime polish
- richer end-to-end demo flows
- more than one worker demo under dual-brain routing
- cleaner coordination surface in final response

### B. Persistence strategy
- define what should persist
- define what should remain ephemeral
- define archive vs. live state boundaries for plurality objects

### C. Operational shell
- operator-facing entry path
- debug/trace room conventions
- safe shell for runtime interaction

### D. Safety hardening
- stronger coordination failure tests
- guardrails for false convergence
- stricter lead/support routing refinement

### E. Packaging
- docs completeness
- top-level repo explanation
- install/run path for new collaborators

---

## Near-term roadmap

### Release R1
Packaging / state map / architecture docs / maturity table / next build order

### Release R2
Coordination refinement
- allocator-aware routing
- better hold thresholds
- better surface-disagreement rules

### Release R3
Persistence / archive discipline
- state persistence policy
- disagreement persistence strategy
- child memory persistence strategy

### Release R4
Operator shell
- minimal runtime console or shell
- trace/debug surface
- internal operator workflow

### Release R5
External integration
- Telegram or other external shell
- observability bridge for live runs

---

## Long-term roadmap

### Family expansion
- richer child interaction patterns
- more explicit role grammar
- stronger plural reasoning without collapse

### Advanced observability
- timeline panels
- disagreement heatmaps
- routing frequency summaries
- reconciliation state analytics

### Product surface
- internal research console
- collaboration surface
- semi-autonomous operator workflow

---

## Release principle

Do not ship by feature count.
Ship by boundary integrity.

The project is ready for a release label when:
- the runtime path is inspectable
- disagreement can remain open
- coordination does not fake consensus
- failure modes are named rather than hidden
