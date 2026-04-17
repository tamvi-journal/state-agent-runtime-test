"""Phase 7 integration-focused tests for bounded boundary-policy feedback."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.boundary_persistence_rules import apply_boundary_persistence
from app.boundary_context_bridge import boundary_residue_to_policy_context
from app.policy_gate import policy_gate
from app.schemas import ActiveMode, Band, BoundaryAwarenessResidue, SelfModel


def _self_model() -> SelfModel:
    return SelfModel(
        stability_band=Band.HIGH,
        disruption_level=Band.LOW,
        mode_recommendation=ActiveMode.BASELINE,
        safe_depth=Band.HIGH,
        state_summary="stable",
    )


def _residue(constraint_type: str, response_strategy: str, pressure: str = "low") -> BoundaryAwarenessResidue:
    return BoundaryAwarenessResidue(
        constraint_type=constraint_type,
        response_strategy=response_strategy,
        monitor_surface="policy",
        presentation_pressure=pressure,
        expected_loss=0.9 if constraint_type == "protective_boundary" else 0.1,
        confidence=0.9,
        trace_tag="phase7",
    )


def test_policy_context_feedback_is_bounded_and_not_indefinite_escalation():
    store = {"status": "none"}

    for turn in range(1, 12):
        store = apply_boundary_persistence(
            stored=store,
            new_residue=_residue("protective_boundary", "stay_with_boundary", pressure="high"),
            turn_id=turn,
        )

    # bounded caps (no indefinite accumulation)
    assert store["protective_pressure"] <= 1.0
    assert store["compression_pressure"] <= 1.0
    assert store["false_block_pressure"] <= 1.0

    context = boundary_residue_to_policy_context(store)
    profile = policy_gate(_self_model(), [], boundary_context=context)

    assert profile.anchor_to_objective is True
    assert profile.style in {"mechanism_first", "compressed"}


def test_conflict_priority_false_block_downgrades_protective_signal():
    store = apply_boundary_persistence(
        stored={"status": "none"},
        new_residue=_residue("protective_boundary", "stay_with_boundary"),
        turn_id=1,
    )

    store = apply_boundary_persistence(
        stored=store,
        new_residue=_residue("false_block", "request_re_evaluation"),
        turn_id=2,
    )

    context = boundary_residue_to_policy_context(store)
    profile = policy_gate(_self_model(), [], boundary_context=context)

    assert context.force_anchor_to_objective is False
    assert profile.anchor_to_objective is False
