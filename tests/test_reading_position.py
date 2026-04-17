"""RC2-R1 unit tests for reading_position runtime state."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.reading_position import update_reading_position
from app.schemas import Band, BoundaryPolicyContext, ReadingPositionState, StateRegister
from app.session_store import SessionStore


def _state(turn_id: int, drift: float, coherence: float = 0.8) -> StateRegister:
    return StateRegister(
        session_id="s1",
        turn_id=turn_id,
        coherence=coherence,
        drift=drift,
        tool_overload=0.0,
        context_fragmentation=0.0,
        active_mode="baseline",
    )


def test_reading_position_is_initialized(tmp_path):
    store = SessionStore(str(tmp_path / "sessions"))
    store.start_session("s1")

    rp = store.load_reading_position()
    assert rp.preferred_zoom == "practical"
    assert rp.stable_preferred_zoom == "practical"
    assert rp.ambiguity_tolerance == Band.MEDIUM


def test_reading_position_shifts_after_boundary_aware_turn():
    shifted = update_reading_position(
        prior=ReadingPositionState.to_initial(),
        current_state=_state(turn_id=1, drift=0.05),
        boundary_context=BoundaryPolicyContext(
            has_boundary_residue=True,
            prefer_style="mechanism_first",
            confidence=0.9,
        ),
    )

    assert shifted.preferred_zoom == "mechanism"
    assert shifted.boundary_sensitivity == Band.HIGH
    assert shifted.ambiguity_tolerance == Band.LOW


def test_reading_position_recovers_toward_stable_mode_after_mild_drift():
    shifted = ReadingPositionState(
        preferred_zoom="mechanism",
        stable_preferred_zoom="practical",
        ambiguity_tolerance=Band.LOW,
        boundary_sensitivity=Band.HIGH,
        last_turn_id=2,
    )

    recovered = update_reading_position(
        prior=shifted,
        current_state=_state(turn_id=3, drift=0.2, coherence=0.75),
        boundary_context=BoundaryPolicyContext(),
    )

    assert recovered.preferred_zoom == "practical"
    assert recovered.boundary_sensitivity == Band.MEDIUM
    assert recovered.ambiguity_tolerance == Band.MEDIUM
