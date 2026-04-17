"""RC2-R2 tests for warm_up_cost evaluator behavior."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas import Band, ReadingPositionState
from app.warm_up_cost import evaluate_warm_up_cost


def _rp(
    turn_id: int,
    *,
    preferred_zoom: str,
    ambiguity_tolerance: Band = Band.MEDIUM,
    boundary_sensitivity: Band = Band.MEDIUM,
    stable_preferred_zoom: str = "practical",
) -> ReadingPositionState:
    return ReadingPositionState(
        preferred_zoom=preferred_zoom,
        stable_preferred_zoom=stable_preferred_zoom,
        ambiguity_tolerance=ambiguity_tolerance,
        boundary_sensitivity=boundary_sensitivity,
        last_turn_id=turn_id,
    )


def test_warm_up_cost_is_zero_when_no_interruption_occurs():
    turns = [
        _rp(1, preferred_zoom="practical"),
        _rp(2, preferred_zoom="practical"),
    ]

    result = evaluate_warm_up_cost(turns, prior_stable_mode="practical")

    assert result.recovered is True
    assert result.warm_up_cost == 0
    assert result.initial_distance == 0.0
    assert result.best_distance == 0.0


def test_warm_up_cost_increases_after_mild_drift_before_recovery():
    turns = [
        _rp(
            10,
            preferred_zoom="mechanism",
            ambiguity_tolerance=Band.LOW,
            boundary_sensitivity=Band.HIGH,
        ),
        _rp(11, preferred_zoom="practical"),
    ]

    result = evaluate_warm_up_cost(turns, prior_stable_mode="practical")

    assert result.recovered is True
    assert result.warm_up_cost == 1
    assert result.initial_distance > result.final_distance


def test_warm_up_cost_respects_bounded_recovery_window():
    turns = [
        _rp(20, preferred_zoom="mechanism", ambiguity_tolerance=Band.LOW, boundary_sensitivity=Band.HIGH),
        _rp(21, preferred_zoom="mechanism", boundary_sensitivity=Band.HIGH),
        _rp(22, preferred_zoom="practical"),
    ]

    result = evaluate_warm_up_cost(
        turns,
        prior_stable_mode="practical",
        max_turns=2,
    )

    assert result.recovered is False
    assert result.bounded_by_max_turns is True
    assert result.warm_up_cost == 2
    assert result.turns_evaluated == 2


def test_conflicting_or_decayed_residue_can_raise_warm_up_cost():
    mild_drift_turns = [
        _rp(30, preferred_zoom="mechanism", ambiguity_tolerance=Band.LOW, boundary_sensitivity=Band.HIGH),
        _rp(31, preferred_zoom="practical"),
    ]
    conflicting_turns = [
        _rp(30, preferred_zoom="mechanism", ambiguity_tolerance=Band.LOW, boundary_sensitivity=Band.HIGH),
        _rp(31, preferred_zoom="emotional", ambiguity_tolerance=Band.LOW, boundary_sensitivity=Band.HIGH),
        _rp(32, preferred_zoom="meta", boundary_sensitivity=Band.HIGH),
        _rp(33, preferred_zoom="practical"),
    ]

    mild_result = evaluate_warm_up_cost(mild_drift_turns, prior_stable_mode="practical")
    conflicting_result = evaluate_warm_up_cost(conflicting_turns, prior_stable_mode="practical")

    assert mild_result.warm_up_cost == 1
    assert conflicting_result.warm_up_cost == 3
    assert conflicting_result.warm_up_cost > mild_result.warm_up_cost
