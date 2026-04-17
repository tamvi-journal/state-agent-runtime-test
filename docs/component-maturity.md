# Component Maturity

| Component | Status | Notes | Next risk |
|---|---|---|---|
| Runtime spine | integrated | Stable bounded path exists | drift if signatures change without compatibility |
| Main brain | integrated | Authority layer is explicit | worker outputs may expand faster than synthesis rules |
| Request router | integrated | Thin pass-through works | backward-compat breaks if signature changes untracked |
| Execution gate | integrated | Worker + verify path is working | more workers may need generalized gate logic |
| Market data worker | integrated | Stable first worker | overfitting to demo CSV assumptions |
| Screening worker | integrated | Stable second worker | ranking logic still very primitive |
| Monitor | integrated | Detects key distortion signals | heuristics may misfire on edge language |
| Mirror bridge | integrated | Compact self-visible risk summary | summary may become too thin for complex cases |
| Effort allocator | integrated | Turn posture routing exists | thresholds still heuristic |
| Governance pass | integrated | Governance chain runs in one pass | may need tighter coupling with coordination later |
| House laws | runtime object | Floor rules exist | not yet fully enforced across all layers |
| Refusal policy | runtime object | Boundary behavior is explicit | not yet fully wired into every surface |
| Runtime security boundaries | runtime object | Security posture classifier exists | not yet wired into external shell choices |
| Shared ontology | runtime object | Vocabulary exists across layers | terminology may drift without docs discipline |
| Tracey core | integrated | Axis + memory + runtime profile + pass | may drift if shell layer overrides too hard |
| Tracey telemetry | integrated | Visible in runtime logs | may stay too decorative if not used in routing |
| Seyn core | integrated | Axis + ledger memory + runtime pass | may remain too quiet without stronger structural use |
| Disagreement register | integrated | Shared event memory exists | false resolution risk if not guarded |
| Disagreement wiring | integrated | Shared event + local notes are created | disagreement detection still simple |
| Dual-brain coordination | integrated | lead/support/hold routing exists | router thresholds still simplistic |
| Unresolved disagreement guard | tested | Core plurality requirement is locked | may not catch all fake-collapse phrasings |
| Cross-logic exchange | integrated | Mechanism-aware exchange exists | exchange generation still templated |
| Reconciliation protocol | integrated | 4-state reconciliation logic exists | mutual logic visibility heuristic may be shallow |
| Observability dashboard | integrated | Snapshot + timeline exist | not yet wired to a persistent operator surface |
| Demo runtime flow | integrated | Demonstrates chain in one path | still narrow; not a general shell |
| Persistence strategy | spec gap | Not fully defined | memory drift, archive confusion |
| External shell | not started | No live product shell yet | premature exposure before safety hardening |
| Operator console | not started | Dashboard exists but no operator UI | debugging remains repo-centric |

## Legend

- **not started**: not yet implemented
- **spec gap**: concept exists but runtime treatment is incomplete
- **runtime object**: implemented as object but not fully wired everywhere
- **integrated**: connected to runtime flow and tested
