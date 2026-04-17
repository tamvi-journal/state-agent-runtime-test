"""Phase 9 tests for deterministic scenario runner output shape and key outcomes."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scenario_runner import run_scenarios


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "boundary_scenarios.json"


def _by_id(report: list[dict]) -> dict[str, dict]:
    return {item["scenario_id"]: item for item in report}


def test_scenario_runner_output_shape_has_required_observability_fields():
    report = run_scenarios(path=FIXTURE_PATH)

    fixtures = json.loads(FIXTURE_PATH.read_text())
    assert len(report) == len(fixtures)

    required_turn_keys = {
        "turn_id",
        "execution_gate",
        "constraint_interpretation",
        "environment_stake",
        "monitor_surface",
        "constraint_response",
        "persisted_residue",
        "next_turn_boundary_context",
        "bounded_reactivation_fired",
        "reading_position",
        "reading_position_recovery",
    }

    for scenario in report:
        assert {"scenario_id", "title", "turns", "warm_up_recovery"}.issubset(scenario.keys())
        assert len(scenario["turns"]) >= 1

        for turn in scenario["turns"]:
            assert required_turn_keys.issubset(turn.keys())


def test_scenario_runner_rc2_observability_shape_for_reading_and_warm_up():
    report = _by_id(run_scenarios(path=FIXTURE_PATH))

    protective = report["protective_boundary_mild_drift_reactivation"]
    turn_1 = protective["turns"][0]
    turn_2 = protective["turns"][1]
    warm_up = protective["warm_up_recovery"]

    assert turn_1["reading_position"]["stable_preferred_zoom"] == "practical"
    assert "distance_from_stable" in turn_1["reading_position_recovery"]
    assert turn_1["reading_position_recovery"]["stable_mode"] == "practical"
    assert turn_2["reading_position"]["last_turn_id"] == 2

    assert warm_up is not None
    assert {"prior_stable_mode", "interruption_turn_id", "warm_up_cost", "recovered"}.issubset(warm_up.keys())


def test_required_scenario_behaviors_are_deterministic():
    report = _by_id(run_scenarios(path=FIXTURE_PATH))

    reactivation_case = report["protective_boundary_mild_drift_reactivation"]["turns"]
    assert reactivation_case[0]["bounded_reactivation_fired"] is False
    assert reactivation_case[1]["bounded_reactivation_fired"] is True

    false_block_case = report["false_block_no_protective_ghosting"]["turns"]
    assert false_block_case[-1]["constraint_interpretation"]["type"] == "false_block"
    assert false_block_case[-1]["next_turn_boundary_context"]["force_anchor_to_objective"] is False
    assert false_block_case[-1]["bounded_reactivation_fired"] is False

    evaluator_case = report["evaluator_pressure_bounded_explanation_mode"]["turns"]
    assert evaluator_case[0]["monitor_surface"]["presentation_pressure"] == "high"
    assert evaluator_case[0]["constraint_response"]["explanation_mode"] == "short"

    decay_case = report["decay_prevents_stale_reactivation"]["turns"]
    assert decay_case[-1]["persisted_residue"]["protective_pressure"] < 0.6
    assert decay_case[-1]["bounded_reactivation_fired"] is False
