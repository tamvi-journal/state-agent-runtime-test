"""Tests for delta log computation."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas import StateRegister, StateDelta, ActiveMode


def test_delta_from_states():
    """Test computing delta between two state registers."""
    prior = StateRegister(
        session_id="test", turn_id=2,
        coherence=0.88, drift=0.03,
        tool_overload=0.00, context_fragmentation=0.08,
    )
    new = StateRegister(
        session_id="test", turn_id=3,
        coherence=0.35, drift=0.78,
        tool_overload=0.45, context_fragmentation=0.72,
        active_mode=ActiveMode.RECOVERY,
    )

    delta = StateDelta.from_states(prior, new, cause_hint="drift_injection")

    assert delta.turn_id == 3
    assert delta.delta_coherence == round(0.35 - 0.88, 4)  # -0.53
    assert delta.delta_drift == round(0.78 - 0.03, 4)       # +0.75
    assert delta.delta_tool_overload == round(0.45, 4)       # +0.45
    assert delta.prior_mode == ActiveMode.BASELINE
    assert delta.new_mode == ActiveMode.RECOVERY
    assert delta.cause_hint == "drift_injection"
    print("✓ test_delta_from_states passed")


def test_delta_zero_change():
    """Test that stable states produce near-zero deltas."""
    s1 = StateRegister(
        session_id="test", turn_id=1,
        coherence=0.80, drift=0.05,
        tool_overload=0.00, context_fragmentation=0.10,
    )
    s2 = StateRegister(
        session_id="test", turn_id=2,
        coherence=0.82, drift=0.04,
        tool_overload=0.00, context_fragmentation=0.11,
    )

    delta = StateDelta.from_states(s1, s2)

    assert abs(delta.delta_coherence) < 0.05
    assert abs(delta.delta_drift) < 0.05
    assert delta.delta_tool_overload == 0.0
    assert abs(delta.delta_context_fragmentation) < 0.05
    assert delta.prior_mode == delta.new_mode
    print("✓ test_delta_zero_change passed")


def test_delta_recovery():
    """Test that recovery shows positive coherence delta."""
    disrupted = StateRegister(
        session_id="test", turn_id=3,
        coherence=0.35, drift=0.78,
        tool_overload=0.45, context_fragmentation=0.72,
        active_mode=ActiveMode.RECOVERY,
    )
    recovering = StateRegister(
        session_id="test", turn_id=4,
        coherence=0.62, drift=0.22,
        tool_overload=0.10, context_fragmentation=0.38,
        active_mode=ActiveMode.CAUTIOUS,
    )

    delta = StateDelta.from_states(disrupted, recovering)

    assert delta.delta_coherence > 0     # recovering
    assert delta.delta_drift < 0         # drift decreasing
    assert delta.delta_tool_overload < 0 # overload decreasing
    assert delta.prior_mode == ActiveMode.RECOVERY
    assert delta.new_mode == ActiveMode.CAUTIOUS
    print("✓ test_delta_recovery passed")


if __name__ == "__main__":
    test_delta_from_states()
    test_delta_zero_change()
    test_delta_recovery()
    print("\nAll delta log tests passed.")
