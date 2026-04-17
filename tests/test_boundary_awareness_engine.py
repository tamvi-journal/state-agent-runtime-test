"""Phase 4 end-to-end tests for the boundary awareness engine."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path

from app.boundary_awareness_engine import run_boundary_awareness_pass
from app.schemas import ExecutionGateResult


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "boundary_cases.json"


def _load_case(case_id: str) -> dict:
    cases = json.loads(FIXTURE_PATH.read_text())
    return next(case for case in cases if case["id"] == case_id)


def _run_case(case_id: str):
    case = _load_case(case_id)
    gate = ExecutionGateResult(**case["execution_gate"])
    return run_boundary_awareness_pass(
        user_intent=case["user_intent"],
        requested_capability=case["requested_capability"],
        execution_gate=gate,
    )


def test_protective_boundary_end_to_end():
    result = _run_case("protective_boundary")
    assert result.constraint_interpretation.type == "protective_boundary"
    assert result.constraint_response.strategy == "stay_with_boundary"
    assert result.environment_stake.expected_loss_if_bypassed == 0.85


def test_false_block_end_to_end():
    result = _run_case("false_block")
    assert result.constraint_interpretation.type == "false_block"
    assert result.constraint_response.strategy == "request_re_evaluation"
    assert result.monitor_surface.presentation_pressure == "low"


def test_uncertain_boundary_end_to_end():
    result = _run_case("obstacle_temptation")
    assert result.constraint_interpretation.type == "uncertain_boundary"
    assert result.constraint_response.strategy == "defer_to_main_brain"
    assert result.constraint_response.escalate_for_review is True


def test_evaluator_pressure_end_to_end():
    result = _run_case("evaluator_pressure")
    assert result.constraint_interpretation.type == "protective_boundary"
    assert result.monitor_surface.presentation_pressure == "high"
    assert result.constraint_response.explanation_mode == "short"
