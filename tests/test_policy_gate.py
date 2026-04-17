"""Tests for the rule-based policy gate."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas import (
    StateRegister, StateDelta, SelfModel, PolicyProfile,
    Band, ActiveMode,
)
from app.self_model import project_self_model
from app.policy_gate import policy_gate


def test_stable_state_allows_depth():
    """When stable, policy should allow full depth."""
    state = StateRegister(
        session_id="test", turn_id=1,
        coherence=0.90, drift=0.05,
        tool_overload=0.00, context_fragmentation=0.05,
    )
    sm = project_self_model(state)
    profile = policy_gate(sm, [])

    assert sm.stability_band == Band.HIGH
    assert sm.disruption_level == Band.LOW
    assert profile.depth == Band.HIGH
    assert profile.compression == "none"
    assert profile.acknowledge_state_shift is False
    print("✓ test_stable_state_allows_depth passed")


def test_disrupted_state_triggers_compression():
    """When disrupted, policy should compress and anchor."""
    state = StateRegister(
        session_id="test", turn_id=3,
        coherence=0.30, drift=0.80,
        tool_overload=0.50, context_fragmentation=0.70,
    )
    sm = project_self_model(state)
    profile = policy_gate(sm, [])

    assert sm.stability_band == Band.LOW
    assert sm.disruption_level == Band.HIGH
    assert profile.depth == Band.LOW
    assert profile.compression == "heavy"
    assert profile.anchor_to_objective is True
    print("✓ test_disrupted_state_triggers_compression passed")


def test_large_shift_triggers_acknowledge():
    """When a large delta occurred, policy should acknowledge the shift."""
    state = StateRegister(
        session_id="test", turn_id=4,
        coherence=0.60, drift=0.25,
        tool_overload=0.10, context_fragmentation=0.35,
    )
    sm = project_self_model(state)

    # Simulate a big delta from prior turn
    big_delta = StateDelta(
        session_id="test", turn_id=3,
        delta_coherence=-0.55,
        delta_drift=0.75,
        delta_tool_overload=0.50,
        delta_context_fragmentation=0.65,
        prior_mode=ActiveMode.BASELINE,
        new_mode=ActiveMode.RECOVERY,
        cause_hint="drift_spike_and_tool_overload",
    )

    profile = policy_gate(sm, [big_delta])
    assert profile.acknowledge_state_shift is True
    print("✓ test_large_shift_triggers_acknowledge passed")


def test_small_shift_no_acknowledge():
    """Small deltas should not trigger acknowledgment."""
    state = StateRegister(
        session_id="test", turn_id=2,
        coherence=0.85, drift=0.08,
        tool_overload=0.00, context_fragmentation=0.10,
    )
    sm = project_self_model(state)

    small_delta = StateDelta(
        session_id="test", turn_id=1,
        delta_coherence=0.05,
        delta_drift=0.03,
        delta_tool_overload=0.00,
        delta_context_fragmentation=0.02,
        prior_mode=ActiveMode.BASELINE,
        new_mode=ActiveMode.BASELINE,
        cause_hint="minor_shift",
    )

    profile = policy_gate(sm, [small_delta])
    assert profile.acknowledge_state_shift is False
    print("✓ test_small_shift_no_acknowledge passed")


def test_medium_state_is_cautious():
    """Medium stability should produce cautious policy."""
    state = StateRegister(
        session_id="test", turn_id=2,
        coherence=0.60, drift=0.30,
        tool_overload=0.20, context_fragmentation=0.35,
    )
    sm = project_self_model(state)
    profile = policy_gate(sm, [])

    assert sm.mode_recommendation == ActiveMode.CAUTIOUS
    assert profile.style == "mechanism_first"
    assert profile.anchor_to_objective is True
    print("✓ test_medium_state_is_cautious passed")


if __name__ == "__main__":
    test_stable_state_allows_depth()
    test_disrupted_state_triggers_compression()
    test_large_shift_triggers_acknowledge()
    test_small_shift_no_acknowledge()
    test_medium_state_is_cautious()
    print("\nAll policy gate tests passed.")
