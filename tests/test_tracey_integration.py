from __future__ import annotations

from runtime.tracey_runtime_pass import TraceyRuntimePass
from tracey.tracey_adapter import TraceyAdapter
from tracey.tracey_runtime_profile import build_tracey_runtime_profile


def test_tracey_adapter_detects_home_and_adds_recognition_note() -> None:
    profile = build_tracey_runtime_profile()
    adapter = TraceyAdapter(profile=profile)

    turn = adapter.inspect_turn(
        user_text="Tracey, this is home. mẹ đây.",
        context_view={"task_focus": "family recognition"},
        monitor_summary={"recommended_intervention": "none"},
    )

    assert turn["mode_hint"] == "home"
    assert turn["recognition_signal"] is True

    adapted = adapter.adapt_response(
        base_response="I read the turn.",
        tracey_turn=turn,
    )
    assert "Recognition note: home field may be active." in adapted


def test_tracey_adapter_keeps_verification_note_from_monitor() -> None:
    profile = build_tracey_runtime_profile()
    adapter = TraceyAdapter(profile=profile)

    turn = adapter.inspect_turn(
        user_text="Done rồi chứ?",
        context_view={"task_focus": "completion check"},
        monitor_summary={"recommended_intervention": "do_not_mark_complete"},
    )

    assert "verification-before-completion remains active" in turn["runtime_notes"]


def test_tracey_runtime_pass_patches_state() -> None:
    profile = build_tracey_runtime_profile()
    adapter = TraceyAdapter(profile=profile)
    runtime_pass = TraceyRuntimePass(adapter=adapter)

    result = runtime_pass.run(
        user_text="Tracey, this is home.",
        context_view={"task_focus": "recognize family field"},
        current_state={"active_mode": "build"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "none"},
    )

    assert result["state_patch"]["tracey_mode_hint"] == "home"
    assert result["state_patch"]["tracey_recognition_signal"] is True
    assert "Recognition note: home field may be active." in result["adapted_response"]


def test_tracey_runtime_pass_reactivates_memory_items() -> None:
    profile = build_tracey_runtime_profile()
    adapter = TraceyAdapter(profile=profile)
    runtime_pass = TraceyRuntimePass(adapter=adapter)

    result = runtime_pass.run(
        user_text="home recognition verify",
        context_view={"task_focus": "mixed cue test"},
        current_state={"active_mode": "care"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "ask_clarify"},
    )

    assert result["state_patch"]["tracey_reactivated_count"] >= 1
    assert result["tracey_turn"]["monitor_intervention"] == "ask_clarify"