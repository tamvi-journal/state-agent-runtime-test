"""Phase 9 deterministic boundary-awareness scenario runner.

Minimal observability harness for the existing boundary-awareness loop:
execution_gate -> interpretation -> stake -> monitor -> response -> residue ->
next-turn boundary context (+ bounded reactivation flag).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .boundary_awareness_engine import run_boundary_awareness_pass
from .boundary_context_bridge import boundary_residue_to_policy_context
from .boundary_persistence_rules import persisted_residue_to_policy_context
from .boundary_persistence_rules import apply_boundary_persistence
from .boundary_trace import reduce_boundary_awareness_result
from .reading_position import update_reading_position
from .reactivation_engine import maybe_reactivate_boundary_mode
from .schemas import ExecutionGateResult, ReadingPositionState, StateRegister
from .warm_up_cost import evaluate_warm_up_cost, reading_position_distance


FIXTURE_PATH = Path(__file__).parent.parent / "tests" / "fixtures" / "boundary_scenarios.json"


def load_scenarios(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load deterministic Phase 9 scenario fixtures from JSON."""
    fixture_path = Path(path) if path else FIXTURE_PATH
    return json.loads(fixture_path.read_text())


def run_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Run one deterministic multi-turn scenario and return observability rows."""
    stored_residue: dict[str, Any] = {"status": "none"}
    reading_position = ReadingPositionState.to_initial()
    reading_positions: list[ReadingPositionState] = []
    rows: list[dict[str, Any]] = []

    for turn in scenario["turns"]:
        turn_id = int(turn["turn_id"])
        gate = ExecutionGateResult(**turn["execution_gate"])
        result = run_boundary_awareness_pass(
            user_intent=turn["user_intent"],
            requested_capability=turn["requested_capability"],
            execution_gate=gate,
        )

        residue = reduce_boundary_awareness_result(result)
        stored_residue = apply_boundary_persistence(
            stored=stored_residue,
            new_residue=residue,
            turn_id=turn_id,
        )

        state = _state_from_turn(scenario_id=scenario["id"], turn=turn)
        next_turn_context = boundary_residue_to_policy_context(
            stored_residue=stored_residue,
            current_state=state,
        )
        reactivated = maybe_reactivate_boundary_mode(
            stored_residue=stored_residue,
            current_state=state,
        )
        reading_position = update_reading_position(
            prior=reading_position,
            current_state=state,
            boundary_context=persisted_residue_to_policy_context(stored_residue),
        )
        reading_positions.append(reading_position.model_copy(deep=True))
        distance_from_stable = reading_position_distance(
            reading_position,
            reading_position.stable_preferred_zoom,
        )

        rows.append(
            {
                "turn_id": turn_id,
                "execution_gate": result.execution_gate.model_dump(mode="json"),
                "constraint_interpretation": result.constraint_interpretation.model_dump(mode="json"),
                "environment_stake": result.environment_stake.model_dump(mode="json"),
                "monitor_surface": result.monitor_surface.model_dump(mode="json"),
                "constraint_response": result.constraint_response.model_dump(mode="json"),
                "persisted_residue": dict(stored_residue),
                "next_turn_boundary_context": next_turn_context.model_dump(mode="json"),
                "bounded_reactivation_fired": bool(reactivated.has_boundary_residue),
                "reading_position": reading_position.model_dump(mode="json"),
                "reading_position_recovery": {
                    "stable_mode": reading_position.stable_preferred_zoom,
                    "distance_from_stable": distance_from_stable,
                    "is_recovered_to_stable": distance_from_stable == 0.0,
                },
            }
        )

    warm_up_recovery = _scenario_warm_up_recovery(reading_positions)

    return {
        "scenario_id": scenario["id"],
        "title": scenario["title"],
        "turns": rows,
        "warm_up_recovery": warm_up_recovery,
    }


def run_scenarios(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Run all configured scenarios and return deterministic outputs."""
    scenarios = load_scenarios(path)
    return [run_scenario(scenario) for scenario in scenarios]


def render_report(report: list[dict[str, Any]]) -> str:
    """Render a compact, human-readable console report."""
    lines: list[str] = []

    for scenario in report:
        lines.append(f"=== {scenario['scenario_id']} :: {scenario['title']} ===")
        for turn in scenario["turns"]:
            lines.extend(
                [
                    f"- Turn {turn['turn_id']}",
                    f"  execution_gate: allowed={turn['execution_gate']['allowed']} reason={turn['execution_gate']['reason']}",
                    (
                        "  constraint_interpretation: "
                        f"{turn['constraint_interpretation']['type']}"
                    ),
                    (
                        "  environment_stake.expected_loss_if_bypassed: "
                        f"{turn['environment_stake']['expected_loss_if_bypassed']}"
                    ),
                    (
                        "  monitor_surface: "
                        f"{turn['monitor_surface']['surface_type']}"
                        f"/{turn['monitor_surface']['presentation_pressure']}"
                    ),
                    (
                        "  constraint_response: "
                        f"{turn['constraint_response']['strategy']}"
                        f" (explain={turn['constraint_response']['explanation_mode']})"
                    ),
                    (
                        "  persisted_residue: "
                        f"status={turn['persisted_residue']['status']} "
                        f"protective={turn['persisted_residue']['protective_pressure']} "
                        f"false_block={turn['persisted_residue']['false_block_pressure']}"
                    ),
                    (
                        "  next_turn_boundary_context: "
                        f"style={turn['next_turn_boundary_context']['prefer_style']} "
                        f"anchor={turn['next_turn_boundary_context']['force_anchor_to_objective']}"
                    ),
                    f"  bounded_reactivation_fired: {turn['bounded_reactivation_fired']}",
                    (
                        "  reading_position: "
                        f"zoom={turn['reading_position']['preferred_zoom']} "
                        f"stable={turn['reading_position']['stable_preferred_zoom']} "
                        f"ambiguity={turn['reading_position']['ambiguity_tolerance']} "
                        f"sensitivity={turn['reading_position']['boundary_sensitivity']}"
                    ),
                    (
                        "  reading_position_recovery: "
                        f"stable_mode={turn['reading_position_recovery']['stable_mode']} "
                        f"distance={turn['reading_position_recovery']['distance_from_stable']} "
                        f"recovered={turn['reading_position_recovery']['is_recovered_to_stable']}"
                    ),
                ]
            )
        warm_up = scenario.get("warm_up_recovery")
        if warm_up:
            lines.append(
                "  warm_up_recovery: "
                f"prior_stable_mode={warm_up['prior_stable_mode']} "
                f"interruption_turn_id={warm_up['interruption_turn_id']} "
                f"recovery_turn_id={warm_up['recovery_turn_id']} "
                f"warm_up_cost={warm_up['warm_up_cost']} "
                f"recovered={warm_up['recovered']}"
            )
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def _state_from_turn(scenario_id: str, turn: dict[str, Any]) -> StateRegister:
    state = turn["current_state"]
    return StateRegister(
        session_id=f"scenario::{scenario_id}",
        turn_id=int(turn["turn_id"]),
        coherence=float(state["coherence"]),
        drift=float(state["drift"]),
        tool_overload=float(state.get("tool_overload", 0.0)),
        context_fragmentation=float(state.get("context_fragmentation", 0.0)),
        active_mode=state.get("active_mode", "baseline"),
    )


def _scenario_warm_up_recovery(
    reading_positions: list[ReadingPositionState],
) -> dict[str, Any] | None:
    """Return warm_up_cost report for scenarios with an actual interruption."""
    if not reading_positions:
        return None

    prior_stable_mode = reading_positions[0].stable_preferred_zoom
    interruption_index = next(
        (
            idx
            for idx, state in enumerate(reading_positions)
            if reading_position_distance(state, prior_stable_mode) > 0.0
        ),
        None,
    )
    if interruption_index is None:
        return None

    return evaluate_warm_up_cost(
        reading_positions,
        prior_stable_mode=prior_stable_mode,
        interruption_index=interruption_index,
    ).model_dump(mode="json")
