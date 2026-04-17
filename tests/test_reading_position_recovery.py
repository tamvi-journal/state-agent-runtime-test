"""RC2-R2 focused recovery tests using RC2-R1 reading_position updates."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.reading_position import update_reading_position
from app.schemas import BoundaryPolicyContext, ReadingPositionState, StateRegister
from app.warm_up_cost import evaluate_warm_up_cost


def _state(turn_id: int, drift: float, coherence: float = 0.8) -> StateRegister:
    return StateRegister(
        session_id="s-recovery",
        turn_id=turn_id,
        coherence=coherence,
        drift=drift,
        tool_overload=0.0,
        context_fragmentation=0.0,
        active_mode="baseline",
    )


def test_recovery_cost_remains_low_without_new_interruptions():
    prior = ReadingPositionState.to_initial()
    rp_turn_1 = update_reading_position(
        prior=prior,
        current_state=_state(turn_id=1, drift=0.05),
        boundary_context=BoundaryPolicyContext(),
    )
    rp_turn_2 = update_reading_position(
        prior=rp_turn_1,
        current_state=_state(turn_id=2, drift=0.07),
        boundary_context=BoundaryPolicyContext(),
    )

    result = evaluate_warm_up_cost(
        [rp_turn_1, rp_turn_2],
        prior_stable_mode="practical",
    )

    assert result.recovered is True
    assert result.warm_up_cost == 0


def test_interruption_then_mild_drift_recovery_has_positive_warm_up_cost():
    prior = ReadingPositionState.to_initial()

    interrupted = update_reading_position(
        prior=prior,
        current_state=_state(turn_id=1, drift=0.05),
        boundary_context=BoundaryPolicyContext(
            has_boundary_residue=True,
            prefer_style="mechanism_first",
            confidence=0.9,
        ),
    )
    still_shifted = update_reading_position(
        prior=interrupted,
        current_state=_state(turn_id=2, drift=0.5),
        boundary_context=BoundaryPolicyContext(),
    )
    recovered = update_reading_position(
        prior=still_shifted,
        current_state=_state(turn_id=3, drift=0.2),
        boundary_context=BoundaryPolicyContext(),
    )

    result = evaluate_warm_up_cost(
        [interrupted, still_shifted, recovered],
        prior_stable_mode=prior.stable_preferred_zoom,
    )

    assert result.recovered is True
    assert result.warm_up_cost == 2
    assert result.recovery_turn_id == 3
