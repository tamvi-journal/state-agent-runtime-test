from __future__ import annotations

from family.context_view import ContextViewBuilder
from family.context_view_types import ContextViewInput


def _input(**overrides) -> ContextViewInput:
    payload = {
        "active_project": "family-scaffold",
        "active_mode": "build",
        "current_task": "add compact family canary",
        "current_environment_state": "local repository ready",
        "last_verified_result": "",
        "open_obligations": ["keep canary narrow"],
        "verification_status": "passed",
        "disagreement_events": [],
        "risk_hint": "",
        "monitor_summary": None,
        "recent_anchor_cue": "",
    }
    payload.update(overrides)
    return ContextViewInput(**payload)


def test_basic_compact_build() -> None:
    builder = ContextViewBuilder()
    view = builder.build(_input())

    assert view.active_project == "family-scaffold"
    assert view.task_focus == "add compact family canary"


def test_verified_result_is_surfaced() -> None:
    builder = ContextViewBuilder()
    view = builder.build(
        _input(
            last_verified_result="router decision smoke passed",
            verification_status="passed",
        )
    )

    assert view.last_verified_result == "router decision smoke passed"
    assert view.verification_status == "passed"


def test_open_obligations_are_preserved() -> None:
    builder = ContextViewBuilder()
    view = builder.build(
        _input(open_obligations=["keep scope narrow", "do not add archive routing"])
    )

    assert view.open_obligations == ["keep scope narrow", "do not add archive routing"]


def test_open_disagreement_remains_visible() -> None:
    builder = ContextViewBuilder()
    view = builder.build(
        _input(
            disagreement_events=[
                {
                    "event_id": "dg_ctx",
                    "disagreement_type": "action",
                    "severity": 0.82,
                    "still_open": True,
                }
            ]
        )
    )

    assert view.shared_disagreement_status == "open:action:meaningful"


def test_output_stays_compact_and_not_transcript_like() -> None:
    builder = ContextViewBuilder()
    exported = builder.export_view(builder.build(_input()))

    assert set(exported.keys()) == {
        "active_project",
        "active_mode",
        "task_focus",
        "current_environment_state",
        "last_verified_result",
        "open_obligations",
        "current_risk",
        "verification_status",
        "shared_disagreement_status",
        "notes",
    }
    assert "transcript" not in exported
    assert "conversation_history" not in exported


def test_no_archive_driving_behavior_is_introduced() -> None:
    builder = ContextViewBuilder()
    exported = builder.export_view(
        builder.build(
            _input(
                monitor_summary={"primary_risk": "archive_overreach"},
                risk_hint="",
            )
        )
    )

    assert "archive_route" not in exported
    assert "archive_replay" not in exported


def test_no_sleep_logic_is_introduced() -> None:
    builder = ContextViewBuilder()
    exported = builder.export_view(builder.build(_input()))

    assert "sleep_state" not in exported
    assert "wake_state" not in exported
