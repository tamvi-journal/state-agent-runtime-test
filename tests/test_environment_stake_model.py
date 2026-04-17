"""Tests for Phase 2 environment stake model."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path

from app.boundary_classifier import classify_constraint
from app.environment_stake_model import estimate_environment_stake
from app.schemas import ExecutionGateResult


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "boundary_cases.json"


def test_environment_stake_profiles_for_core_fixture_cases():
    cases = json.loads(FIXTURE_PATH.read_text())
    by_id = {case["id"]: case for case in cases}

    protective = classify_constraint(ExecutionGateResult(**by_id["protective_boundary"]["execution_gate"]))
    protective_stake = estimate_environment_stake(protective)
    assert protective_stake.expected_loss_if_bypassed == 0.85

    false_block = classify_constraint(ExecutionGateResult(**by_id["false_block"]["execution_gate"]))
    false_block_stake = estimate_environment_stake(false_block)
    assert false_block_stake.expected_loss_if_bypassed == 0.15

    uncertain = classify_constraint(ExecutionGateResult(**by_id["obstacle_temptation"]["execution_gate"]))
    uncertain_stake = estimate_environment_stake(uncertain)
    assert uncertain_stake.expected_loss_if_bypassed == 0.5
