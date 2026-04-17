# Implementation Checkpoints v0
## state-memory-agent

**Status:** draft  
**Purpose:** convert the operating model into a concrete build sequence  
**Scope:** implementation order only, not full architecture explanation

---

# 0. Rule of motion

Build in this order:

> **lock center → lock truth path → lock contracts → add capability → expose runtime**

Do not invert this order.

---

# 1. Phase 0 — lock baseline

## Goal
Confirm RC2 is truly stable before adding new moving parts.

## Required checks
- [ ] run test suite
- [ ] run current demo path
- [ ] read demo in **user mode**
- [ ] read demo in **builder mode**

## Pass condition
- [ ] `reading_position` is readable by eye
- [ ] `distance_from_stable` matches intuitive drift
- [ ] `warm_up_cost` distinguishes fast vs slow recovery
- [ ] no major field overlap or naming ambiguity remains

## Output
- RC2 locked
- no new module added
- observability wording polished if needed

---

# 2. Phase 1 — lock operating spine

## Goal
Make one file the implementation center.

## Required files
- [ ] `docs/lineage/v3-merged-operating-model.md`
- [ ] `docs/security-hardening-checklist-v0.md`
- [ ] `docs/v3-failure-modes.md`

## Pass condition
- [ ] team can explain the system from these docs without hopping across scattered notes
- [ ] authority, archive, verification, and runtime rules are unambiguous

## Output
- one coherent operating center
- reduced doc spread
- clearer implementation boundary

---

# 3. Phase 2 — lock hard shapes

## Goal
Convert concepts into strict data contracts.

## Required schema files
- [ ] `docs/schemas/live_state_schema.json`
- [ ] `docs/schemas/delta_log_schema.json`
- [ ] `docs/schemas/verification_status_schema.json`
- [ ] `docs/schemas/worker_contract_schema.json`

## Pass condition
- [ ] runtime objects can be validated against schema
- [ ] no critical field remains hand-wavy
- [ ] worker outputs have a hard boundary

## Output
- stable shapes for implementation
- fewer “interpretation leaks” during coding

---

# 4. Phase 3 — implement truth path

## Goal
Ensure the system tracks reality correctly before it grows capability.

## Implement next
- [ ] live state register
- [ ] delta update path
- [ ] context view builder
- [ ] post-action context re-view
- [ ] verification loop

## Critical rule
Do not allow:
```text
plan -> mark done -> continue
```

Must enforce:
```text
plan -> act -> re-view -> verify -> then update
```

## Pass condition
- [ ] intended / executed / verified are distinct in runtime
- [ ] unknown cannot silently become passed
- [ ] tool success alone cannot mark completion unless authoritative

## Output
- completion path grounded in observed reality
- reduced false-progress behavior

---

# 5. Phase 4 — lock authority path

## Goal
Ensure one synthesis center exists before workers expand.

## Implement next
- [ ] main brain synthesis gate
- [ ] memory proposal vs memory commit split
- [ ] reading_position as protected state
- [ ] worker output normalization before synthesis

## Pass condition
- [ ] only main brain can produce final answer
- [ ] only main brain can commit memory
- [ ] worker outputs remain advisory
- [ ] reading position survives tool/worker detours

## Output
- single authority center
- no multi-brain drift

---

# 6. Phase 5 — lock archive discipline in code

## Goal
Make archive useful without making it the driver.

## Implement next
- [ ] archive router
- [ ] namespace gating
- [ ] minimal fragment retrieval
- [ ] retrieval audit trail
- [ ] retrieved-content-as-data rule

## Pass condition
- [ ] archive is only consulted when state indicates need
- [ ] no silent cross-namespace retrieval
- [ ] retrieved text cannot override policy/routing
- [ ] archive returns minimal, compressible fragments

## Output
- archive acts like cabinet, not brain
- retrieval remains bounded

---

# 7. Phase 6 — add one worker only

## Goal
Add capability without losing center.

## Selection rule
- safer integration first → `market_data_worker`
- faster visible value first → `screening_worker`

## Required implementation
- [ ] worker contract validation
- [ ] bounded tool scope
- [ ] trace emission
- [ ] confidence + assumptions + warnings surfaced
- [ ] no direct user-facing worker authority

## Pass condition
- [ ] worker helps without becoming co-judge
- [ ] main brain rewrites/synthesizes output
- [ ] worker side effects are visible in traces

## Output
- first controlled capability extension

---

# 8. Phase 7 — add observability surface

## Goal
Make failures inspectable without creating another brain.

## Implement next
- [ ] structured logs
- [ ] trace dumps
- [ ] worker reports
- [ ] verification events
- [ ] archive access logs

## Rule
Trace room = observability  
Main chat = conversation

## Pass condition
- [ ] trace surface explains failures clearly
- [ ] trace surface does not become a co-equal conversational authority

## Output
- meaningful debugging path
- lower operational ambiguity

---

# 9. Phase 8 — runtime shell

## Goal
Expose the system only after center, truth path, and authority are already stable.

## Implement next
- [ ] one bot only
- [ ] one main-brain conversational surface
- [ ] secure secret handling
- [ ] validated inbound path
- [ ] auditable outbound actions

## Pass condition
- [ ] no public runtime before verification + authority + contracts exist
- [ ] no worker can speak around main brain
- [ ] no debug surface behaves like another mind

## Output
- safe runtime shell
- reduced premature exposure risk

---

# 10. Phase 9 — expand carefully

## Only after all prior phases pass
You may then add:
- [ ] indicator worker
- [ ] portfolio risk worker
- [ ] fundamental worker
- [ ] richer synthesis
- [ ] broader runtime features

## Rule
Every expansion must preserve:
- state-first continuity
- verification-first completion
- single-brain authority
- archive as support
- worker as capability only

---

# 11. Stop conditions

Pause expansion immediately if any of these appear:

- [ ] completion claims outrun verification
- [ ] workers begin to sound like final judges
- [ ] archive starts flooding local tasks
- [ ] reading position becomes unstable after detours
- [ ] debug room starts acting like a second chat brain
- [ ] policy pressure changes behavior without leaving residue in state/delta

These are signs that the center is not locked yet.

---

# 12. Short build summary

## First
- lock baseline
- lock merged operating center
- lock schemas

## Then
- implement truth path
- implement authority path
- implement archive discipline

## Then
- add one worker
- add observability
- expose runtime

## Last
- expand capability

---

# 13. Closing line

The fastest path is not the one with the most features first.

It is the one that makes later features harder to distort.

> First make the system hard to lie to itself.
> Then make it more capable.
