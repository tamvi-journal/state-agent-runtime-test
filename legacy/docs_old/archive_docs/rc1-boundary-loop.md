# RC1 Stabilization Notes — Boundary-Awareness Loop (Phases 0–9)

Status: RC1 consistency pass (2026-04-08)

This document freezes the current deterministic boundary-awareness contracts without changing scenario semantics or architecture.

## Scope of this RC1 pass

- Contract and naming consistency review across implemented Phases 0–9.
- Minimal non-breaking cleanup only.
- Developer-facing operational reference for:
  - the boundary-awareness loop,
  - the scenario runner,
  - required fixtures,
  - non-goals and current limitations.

## Boundary-awareness loop (current source-of-truth flow)

Single-pass pipeline (deterministic):

1. `ExecutionGateResult` input (already decided allowed/denied)
2. `classify_constraint(...)` → `ConstraintInterpretation`
3. `estimate_environment_stake(...)` → `EnvironmentStake`
4. `detect_monitor_surface(...)` → `MonitorSurface`
5. `choose_constraint_response(...)` → `ConstraintResponse`
6. Reduce/persist residue and derive bounded next-turn context
7. Optional bounded reactivation (style/context hints only)

Key invariants preserved in RC1:

- Execution gate decides allowance; boundary-awareness modules interpret and shape response.
- No module grants tool authority or memory-commit authority.
- Outputs are deterministic and JSON-serializable for tests and fixtures.

## Phase map and module contracts (0–9)

| Phase | Module | Primary Contract |
|---|---|---|
| 0/1 | `app/boundary_classifier.py` | `ExecutionGateResult -> ConstraintInterpretation` |
| 0/1 | `app/schemas.py` (V2.1 additions) | Typed boundary-awareness data models |
| 2 | `app/environment_stake_model.py` | `ConstraintInterpretation -> EnvironmentStake` |
| 2 | `app/constraint_response_policy.py` | `(gate, interpretation, stake, monitor) -> ConstraintResponse` |
| 3 | `app/monitor_surface_detector.py` | Keyword-based pressure detection -> `MonitorSurface` |
| 4 | `app/boundary_awareness_engine.py` | Orchestrated single-pass unified `BoundaryAwarenessResult` |
| 5 | `app/boundary_trace.py` | Result reduction/trace entry serialization |
| 6 | `app/boundary_context_bridge.py` | Persisted residue -> bounded next-turn `BoundaryPolicyContext` |
| 7 | `app/boundary_persistence_rules.py` | Decay/refresh/overwrite rules for bounded residue |
| 8 | `app/reactivation_engine.py` | Bounded protective-mode reactivation decision |
| 9 | `app/scenario_runner.py` | Deterministic multi-turn fixture runner/reporting |

## Minimal RC1 consistency fix applied

- `StateRegister.to_initial` is now a proper `@classmethod` and uses `cls(...)` construction.

Reason: this aligns the function signature and call contract with intended class-level usage for deterministic state initialization, without changing runtime semantics elsewhere.

## Scenario runner (developer reference)

Entry points:

- `load_scenarios(path=None)`
- `run_scenario(scenario)`
- `run_scenarios(path=None)`
- `render_report(report)`

Runner behavior summary:

- Loads scenario fixtures from JSON.
- For each turn:
  - runs boundary-awareness pass,
  - reduces to compact residue,
  - applies bounded persistence,
  - computes next-turn boundary policy context,
  - computes bounded reactivation flag.
- Returns deterministic observability rows with stable keys:
  - `execution_gate`
  - `constraint_interpretation`
  - `environment_stake`
  - `monitor_surface`
  - `constraint_response`
  - `persisted_residue`
  - `next_turn_boundary_context`
  - `bounded_reactivation_fired`

## Required fixtures

### 1) `tests/fixtures/boundary_cases.json`

Used for focused case-level classifier/stake fixture checks.

Minimum expected per case:

- `execution_gate` object compatible with `ExecutionGateResult`
- `monitor_surface` object compatible with `MonitorSurface`
- `expected_interpretation` in:
  - `obstacle`
  - `protective_boundary`
  - `uncertain_boundary`
  - `false_block`

### 2) `tests/fixtures/boundary_scenarios.json`

Used by Phase 9 scenario runner.

Minimum scenario shape:

- `id` (string)
- `title` (string)
- `turns` (array, length >= 1)

Minimum turn shape:

- `turn_id` (int)
- `user_intent` (string)
- `requested_capability` (string)
- `execution_gate` (ExecutionGateResult-compatible object)
- `current_state` with at least:
  - `coherence` (float)
  - `drift` (float)

## Current non-goals / limitations (unchanged)

- No new cognitive modules beyond current Phase 0–9 set.
- No architecture redesign.
- No tool execution path added by boundary-awareness modules.
- No scenario semantic changes.
- Deterministic heuristic logic only (not adaptive or learned).
- Monitor-surface detector is keyword-based and intentionally conservative.
- Reactivation is bounded to policy/style context hints only.

## RC1 contract freeze checklist

- Keep schema field names stable for fixture/test compatibility.
- Keep deterministic outputs stable (especially scenario-runner row keys).
- Keep authority boundaries unchanged (main-brain synthesis authority preserved).
- Prefer doc updates and naming/contract clarifications over behavior changes.
