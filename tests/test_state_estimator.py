"""Tests for state estimation and observable signals."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas import StateRegister, ObservableSignals, ActiveMode
from app.state_estimator import compute_observable_signals


def test_observable_signals_basic():
    """Test that observable signals are computed correctly."""
    signals = compute_observable_signals(
        turn_id=1,
        user_message="Hello, help me analyze this data",
        tool_calls=2,
        tool_errors=1,
        user_correction=False,
        context_tokens_used=5000,
        context_tokens_max=128000,
        session_turn_depth=1,
    )
    assert signals.turn_id == 1
    assert signals.user_message_length == len("Hello, help me analyze this data")
    assert signals.tool_calls_this_turn == 2
    assert signals.tool_errors_this_turn == 1
    assert signals.user_correction_detected is False
    print("✓ test_observable_signals_basic passed")


def test_observable_signals_no_tools():
    """Test signals when no tools are called."""
    signals = compute_observable_signals(
        turn_id=3,
        user_message="Just a simple question",
    )
    assert signals.tool_calls_this_turn == 0
    assert signals.tool_errors_this_turn == 0
    assert signals.context_tokens_max == 128000
    print("✓ test_observable_signals_no_tools passed")


def test_state_register_initial():
    """Test creating an initial state register."""
    state = StateRegister(
        session_id="test_001",
        turn_id=0,
        coherence=0.80,
        drift=0.00,
        tool_overload=0.00,
        context_fragmentation=0.00,
    )
    assert state.coherence == 0.80
    assert state.active_mode == ActiveMode.BASELINE
    assert state.policy_pressure_proxy is None
    print("✓ test_state_register_initial passed")


def test_state_register_bounds():
    """Test that state values respect bounds."""
    try:
        StateRegister(
            session_id="test",
            turn_id=0,
            coherence=1.5,  # out of bounds!
        )
        assert False, "Should have raised validation error"
    except Exception:
        pass
    print("✓ test_state_register_bounds passed")


if __name__ == "__main__":
    test_observable_signals_basic()
    test_observable_signals_no_tools()
    test_state_register_initial()
    test_state_register_bounds()
    print("\nAll state estimator tests passed.")
