# Next Build Order

## Recommendation after Packaging R1

### 1. Coordination refinement
Priority: **highest**

Why:
- dual-brain routing already exists
- now the risk is not missing architecture, but simplistic behavior

Focus:
- allocator-aware coordination
- better hold thresholds
- better routing between execution / verify / home / care / audit
- surface-disagreement policy refinement

---

### 2. Persistence / archive discipline
Priority: **high**

Why:
- plurality objects now exist
- disagreement, reconciliation, local notes, child memory, and governance traces need persistence rules

Focus:
- what persists
- what decays
- what archives
- what remains only in live state

---

### 3. Operator-facing shell
Priority: **medium-high**

Why:
- observability already exists
- builders need a practical way to inspect runs without reading raw repo logs only

Focus:
- internal console or debug shell
- dashboard rendering path
- operator run summary

---

### 4. External shell strategy
Priority: **medium**

Why:
- the system is approaching internal alpha completeness
- but external shell before persistence + coordination refinement is risky

Focus:
- Telegram or equivalent surface
- read-only first
- strict operator visibility
- no hidden autonomy

---

### 5. Broader worker/generalization path
Priority: **medium**

Why:
- current runtime is structurally real
- but still centered on narrow demo worker paths

Focus:
- generalize execution gate
- broader worker contracts
- stronger synthesis handling for more result types

---

## Do not prioritize first

These should **not** be next:

### A. More children
Not yet.
Plurality exists; depth beats count.

### B. Fancy UI
Not yet.
Operator visibility should precede aesthetics.

### C. Autonomous orchestration
Not yet.
The system still needs clearer persistence and coordination discipline.

---

## Practical next milestone suggestion

Recommended next internal milestone:

> **R2 — Coordination + Persistence Hardening**

Definition:
- routing gets smarter
- plurality memory gets rules
- operator snapshot becomes more useful
- system stays honest under pressure

That is the strongest next step after packaging.
