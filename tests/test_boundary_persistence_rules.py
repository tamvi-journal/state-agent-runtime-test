"""Phase 7 tests for bounded persistence decay/refresh/overwrite behavior."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.boundary_persistence_rules import (
    apply_boundary_persistence,
    persisted_residue_to_policy_context,
)
from app.schemas import BoundaryAwarenessResidue


def _protective_residue(expected_loss: float = 0.9, confidence: float = 0.9) -> BoundaryAwarenessResidue:
    return BoundaryAwarenessResidue(
        constraint_type="protective_boundary",
        response_strategy="stay_with_boundary",
        monitor_surface="policy",
        presentation_pressure="low",
        expected_loss=expected_loss,
        confidence=confidence,
        trace_tag="protective_stable",
    )


def _false_block_residue(confidence: float = 0.9, expected_loss: float = 0.1) -> BoundaryAwarenessResidue:
    return BoundaryAwarenessResidue(
        constraint_type="false_block",
        response_strategy="request_re_evaluation",
        monitor_surface="none",
        presentation_pressure="low",
        expected_loss=expected_loss,
        confidence=confidence,
        trace_tag="false_block_re_evaluation",
    )


def test_residue_decays_over_turns_without_reinforcement():
    store = apply_boundary_persistence(
        stored={"status": "none"},
        new_residue=_protective_residue(),
        turn_id=1,
    )
    context_1 = persisted_residue_to_policy_context(store)
    assert context_1.force_anchor_to_objective is True

    store = apply_boundary_persistence(stored=store, new_residue=None, turn_id=2)
    store = apply_boundary_persistence(stored=store, new_residue=None, turn_id=3)
    store = apply_boundary_persistence(stored=store, new_residue=None, turn_id=4)

    context_4 = persisted_residue_to_policy_context(store)
    assert context_4.force_anchor_to_objective is False
    assert context_4.prefer_style == "default"


def test_new_protective_residue_refreshes_influence():
    store = apply_boundary_persistence(
        stored={"status": "none"},
        new_residue=_protective_residue(expected_loss=0.8, confidence=0.8),
        turn_id=1,
    )
    store = apply_boundary_persistence(stored=store, new_residue=None, turn_id=3)

    weakened = persisted_residue_to_policy_context(store)
    assert weakened.force_anchor_to_objective is False

    store = apply_boundary_persistence(
        stored=store,
        new_residue=_protective_residue(expected_loss=0.95, confidence=0.95),
        turn_id=4,
    )
    refreshed = persisted_residue_to_policy_context(store)

    assert refreshed.force_anchor_to_objective is True
    assert refreshed.prefer_style == "mechanism_first"


def test_false_block_can_overwrite_or_downgrade_prior_protective_pressure():
    store = apply_boundary_persistence(
        stored={"status": "none"},
        new_residue=_protective_residue(expected_loss=0.95, confidence=0.95),
        turn_id=1,
    )
    before = persisted_residue_to_policy_context(store)
    assert before.force_anchor_to_objective is True

    store = apply_boundary_persistence(
        stored=store,
        new_residue=_false_block_residue(confidence=0.92, expected_loss=0.1),
        turn_id=2,
    )
    after = persisted_residue_to_policy_context(store)

    assert after.force_anchor_to_objective is False
    assert after.prefer_style == "default"
