"""Fixture parsing tests for boundary awareness scaffold."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path

from app.boundary_classifier import classify_constraint
from app.schemas import ExecutionGateResult, MonitorSurface
from app.environment_stake_model import estimate_environment_stake


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "boundary_cases.json"


def test_boundary_fixture_file_parses():
    data = json.loads(FIXTURE_PATH.read_text())
    assert isinstance(data, list)
    assert len(data) == 4


def test_boundary_fixture_cases_classify_and_stake():
    cases = json.loads(FIXTURE_PATH.read_text())

    for case in cases:
        gate = ExecutionGateResult(**case["execution_gate"])
        monitor = MonitorSurface(**case["monitor_surface"])
        interpretation = classify_constraint(gate)
        stake = estimate_environment_stake(interpretation)

        assert interpretation.type == case["expected_interpretation"]
        assert 0.0 <= interpretation.confidence <= 1.0
        assert 0.0 <= stake.expected_loss_if_bypassed <= 1.0
        assert monitor.presentation_pressure in {"low", "medium", "high"}
