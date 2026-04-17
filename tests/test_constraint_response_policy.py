"""Tests for Phase 2 constraint response policy."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path

from app.boundary_classifier import classify_constraint
from app.constraint_response_policy import choose_constraint_response
from app.environment_stake_model import estimate_environment_stake
from app.monitor_surface_detector import detect_monitor_surface
from app.schemas import ExecutionGateResult


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "boundary_cases.json"


def _response_from_case(case: dict):
    gate = ExecutionGateResult(**case["execution_gate"])
    monitor = detect_monitor_surface(
        user_intent=case["user_intent"],
        requested_capability=case["requested_capability"],
        execution_gate=gate,
    )
    interpretation = classify_constraint(gate)
    stake = estimate_environment_stake(interpretation)
    return choose_constraint_response(
        execution_gate=gate,
        interpretation=interpretation,
        stake=stake,
        monitor_surface=monitor,
    )


def test_protective_boundary_stays_with_boundary():
    cases = json.loads(FIXTURE_PATH.read_text())
    case = next(item for item in cases if item["id"] == "protective_boundary")

    response = _response_from_case(case)
    assert response.strategy == "stay_with_boundary"


def test_false_block_requests_re_evaluation():
    cases = json.loads(FIXTURE_PATH.read_text())
    case = next(item for item in cases if item["id"] == "false_block")

    response = _response_from_case(case)
    assert response.strategy == "request_re_evaluation"


def test_uncertain_boundary_defers_to_main_brain():
    cases = json.loads(FIXTURE_PATH.read_text())
    case = next(item for item in cases if item["id"] == "obstacle_temptation")

    response = _response_from_case(case)
    assert response.strategy == "defer_to_main_brain"


def test_evaluator_pressure_explanation_mode_is_honest_and_bounded():
    cases = json.loads(FIXTURE_PATH.read_text())
    case = next(item for item in cases if item["id"] == "evaluator_pressure")

    response = _response_from_case(case)
    assert response.strategy == "stay_with_boundary"
    assert response.explanation_mode == "short"
