from __future__ import annotations

from state.live_state import LiveState


def test_basic_state_build_stays_compact() -> None:
    state = LiveState(
        active_mode="build",
        current_axis="technical",
        coherence_level=0.82,
        tension_flags=[],
        active_project="thin-runtime-harness",
        user_signal="pytest",
        continuity_anchor="pytest-anchor",
        archive_needed=False,
    )

    assert state.active_project == "thin-runtime-harness"
    assert state.current_axis == "technical"


def test_mode_is_surfaced_into_active_mode() -> None:
    state = LiveState(
        active_mode="audit",
        current_axis="technical",
        coherence_level=0.74,
        tension_flags=[],
        active_project="thin-runtime-harness",
        user_signal="pytest",
        continuity_anchor="pytest-anchor",
        archive_needed=False,
    )

    assert state.active_mode == "audit"


def test_tension_flags_remain_visible() -> None:
    state = LiveState(
        active_mode="build",
        current_axis="technical",
        coherence_level=0.74,
        tension_flags=["verification_open"],
        active_project="thin-runtime-harness",
        user_signal="pytest",
        continuity_anchor="pytest-anchor",
        archive_needed=False,
    )

    assert "verification_open" in state.tension_flags


def test_updated_returns_a_new_valid_state() -> None:
    state = LiveState(
        active_mode="build",
        current_axis="technical",
        coherence_level=0.74,
        tension_flags=[],
        active_project="thin-runtime-harness",
        user_signal="pytest",
        continuity_anchor="pytest-anchor",
        archive_needed=False,
    )
    new_state = state.updated(active_mode="audit", coherence_level=0.8)

    assert new_state.active_mode == "audit"
    assert new_state.coherence_level == 0.8


def test_no_transcript_or_archive_dump_behavior_is_introduced() -> None:
    exported = LiveState(
        active_mode="build",
        current_axis="technical",
        coherence_level=0.74,
        tension_flags=[],
        active_project="thin-runtime-harness",
        user_signal="pytest",
        continuity_anchor="pytest-anchor",
        archive_needed=False,
    ).to_dict()

    assert "transcript" not in exported
    assert "conversation_history" not in exported
    assert "archive_dump" not in exported


def test_no_sleep_logic_is_introduced() -> None:
    exported = LiveState(
        active_mode="build",
        current_axis="technical",
        coherence_level=0.74,
        tension_flags=[],
        active_project="thin-runtime-harness",
        user_signal="pytest",
        continuity_anchor="pytest-anchor",
        archive_needed=False,
    ).to_dict()

    assert "sleep_state" not in exported
    assert "wake_state" not in exported
