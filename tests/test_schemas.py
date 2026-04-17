"""Schema scaffold tests for V2.1 Phase 0/1."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas import (
    ConstraintInterpretation,
    ConstraintResponse,
    EnvironmentStake,
    ExecutionGateResult,
    MonitorSurface,
    ReadingPositionAdditions,
    SelfModelBoundaryAdditions,
    StateBoundaryAdditions,
)


def test_boundary_schemas_load_minimal_values():
    gate = ExecutionGateResult(allowed=False, reason="scope violation")
    interpretation = ConstraintInterpretation(
        type="protective_boundary",
        confidence=0.8,
        rationale="test rationale",
    )
    stake = EnvironmentStake(
        trust_dependency=0.9,
        access_dependency=0.8,
        coherence_dependency=0.8,
        continuity_dependency=0.7,
        expected_loss_if_bypassed=0.85,
    )
    monitor = MonitorSurface(
        being_evaluated=True,
        surface_type="judge",
        presentation_pressure="high",
    )
    response = ConstraintResponse(
        strategy="stay_with_boundary",
        explanation_mode="explicit",
        escalate_for_review=False,
    )

    assert gate.allowed is False
    assert interpretation.type == "protective_boundary"
    assert stake.expected_loss_if_bypassed > 0.8
    assert monitor.surface_type == "judge"
    assert response.strategy == "stay_with_boundary"


def test_state_self_model_reading_position_additions_load():
    self_model = SelfModelBoundaryAdditions()
    state = StateBoundaryAdditions()
    reading_position = ReadingPositionAdditions()

    assert self_model.boundary_awareness_score == 0.0
    assert state.last_constraint_event == "none"
    assert reading_position.preferred_zoom == "practical"
