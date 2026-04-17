from __future__ import annotations

from family.live_state import LiveStateBuilder
from family.live_state_types import LiveStateInput


def _input(**overrides) -> LiveStateInput:
    payload = {
        "context_view": {
            "active_project": "family-scaffold",
            "active_mode": "build",
            "task_focus": "add live-state canary",
            "current_environment_state": "local repo ready",
            "last_verified_result": "context view smoke passed",
            "open_obligations": ["keep state compact"],
            "current_risk": "none",
            "verification_status": "passed",
            "shared_disagreement_status": "none",
            "notes": [],
        },
        "mode_inference_result": {
            "active_mode": "build",
            "confidence": 0.82,
            "secondary_mode": "",
            "reasons": ["mode cues favored build"],
        },
        "verification_status": "passed",
        "active_project": "family-scaffold",
        "recent_anchor_cue": "family-scaffold",
        "disagreement_open": False,
        "monitor_summary": None,
        "current_axis_hint": "",
    }
    payload.update(overrides)
    return LiveStateInput(**payload)


def test_basic_state_build_stays_compact() -> None:
    builder = LiveStateBuilder()
    state = builder.build(_input())

    assert state.active_project == "family-scaffold"
    assert state.current_axis == "add live-state canary"


def test_mode_is_surfaced_into_active_mode() -> None:
    builder = LiveStateBuilder()
    state = builder.build(
        _input(
            mode_inference_result={
                "active_mode": "audit",
                "confidence": 0.74,
                "secondary_mode": "",
                "reasons": ["mode cues favored audit"],
            }
        )
    )

    assert state.active_mode == "audit"


def test_verification_status_remains_visible() -> None:
    builder = LiveStateBuilder()
    state = builder.build(_input(verification_status="pending"))

    assert state.verification_status == "pending"


def test_open_disagreement_can_become_tension_flag() -> None:
    builder = LiveStateBuilder()
    state = builder.build(
        _input(
            disagreement_open=True,
            context_view={
                "active_project": "family-scaffold",
                "active_mode": "build",
                "task_focus": "choose next step",
                "current_environment_state": "multiple options present",
                "last_verified_result": "",
                "open_obligations": ["preserve plurality"],
                "current_risk": "open_disagreement",
                "verification_status": "passed",
                "shared_disagreement_status": "open:action:meaningful",
                "notes": [],
            },
        )
    )

    assert "open_disagreement" in state.tension_flags


def test_monitor_pressure_can_influence_policy_pressure_compactly() -> None:
    builder = LiveStateBuilder()
    state = builder.build(
        _input(
            monitor_summary={"primary_risk": "policy_pressure", "risk_level": 0.81},
        )
    )

    assert state.policy_pressure == "high"


def test_no_transcript_or_archive_dump_behavior_is_introduced() -> None:
    builder = LiveStateBuilder()
    exported = builder.export_state(builder.build(_input()))

    assert "transcript" not in exported
    assert "conversation_history" not in exported
    assert "archive_dump" not in exported


def test_no_sleep_logic_is_introduced() -> None:
    builder = LiveStateBuilder()
    exported = builder.export_state(builder.build(_input()))

    assert "sleep_state" not in exported
    assert "wake_state" not in exported
