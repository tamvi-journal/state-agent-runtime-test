from __future__ import annotations

from family.reactivation_layer import ReactivationLayer
from family.reactivation_types import ReactivationInput


def _input(**overrides) -> ReactivationInput:
    payload = {
        "current_message": "Please continue the family scaffold work for family-scaffold.",
        "detected_cues": ["family-scaffold", "continue build"],
        "active_project_hint": "family-scaffold",
        "compression_summary": {
            "active_question": "continue the family scaffold",
            "main_points": ["project: family-scaffold", "mode: build", "verification: passed"],
            "caution": "",
            "anchor_cue": "family-scaffold",
            "next_state_hint": "continue_build",
        },
        "context_view": {
            "active_project": "family-scaffold",
            "active_mode": "build",
            "task_focus": "continue the family scaffold",
        },
        "live_state": {
            "active_mode": "build",
            "current_axis": "continue the family scaffold",
            "coherence_level": "stable",
            "active_project": "family-scaffold",
        },
        "recent_anchor_cue": "family-scaffold",
        "disagreement_open": False,
        "verification_status": "passed",
        "mode_hint": "",
    }
    payload.update(overrides)
    return ReactivationInput(**payload)


def test_strong_anchor_project_cue_can_trigger_reactivation() -> None:
    layer = ReactivationLayer()
    result = layer.build(_input())

    assert result.reactivation_triggered is True
    assert result.restored_project == "family-scaffold"


def test_restored_mode_can_be_recovered_from_compact_cues() -> None:
    layer = ReactivationLayer()
    result = layer.build(_input())

    assert result.restored_mode == "build"


def test_unresolved_disagreement_lowers_confidence() -> None:
    layer = ReactivationLayer()
    base = layer.build(_input())
    lowered = layer.build(_input(disagreement_open=True))

    assert lowered.confidence < base.confidence


def test_unsettled_verification_lowers_confidence() -> None:
    layer = ReactivationLayer()
    base = layer.build(_input())
    lowered = layer.build(_input(verification_status="pending"))

    assert lowered.confidence < base.confidence


def test_weak_no_cue_does_not_force_strong_restoration() -> None:
    layer = ReactivationLayer()
    result = layer.build(
        _input(
            current_message="Hello there.",
            detected_cues=[],
            active_project_hint="",
            recent_anchor_cue="",
            compression_summary={
                "active_question": "continue the family scaffold",
                "main_points": [],
                "caution": "",
                "anchor_cue": "",
                "next_state_hint": "continue_build",
            },
            context_view={"active_project": "", "active_mode": "", "task_focus": ""},
            live_state={"active_mode": "", "current_axis": "", "coherence_level": "mixed", "active_project": ""},
        )
    )

    assert result.reactivation_triggered is False or result.confidence < 0.50


def test_output_remains_compact_and_history_free() -> None:
    layer = ReactivationLayer()
    exported = layer.export_result(layer.build(_input()))

    assert set(exported.keys()) == {
        "reactivation_triggered",
        "matched_cues",
        "restored_mode",
        "restored_axis_hint",
        "restored_project",
        "confidence",
        "notes",
    }
    assert "transcript" not in exported
    assert "history" not in exported


def test_no_archive_routing_is_introduced() -> None:
    layer = ReactivationLayer()
    exported = layer.export_result(layer.build(_input()))

    assert "archive_route" not in exported
    assert "archive_replay" not in exported


def test_no_sleep_logic_is_introduced() -> None:
    layer = ReactivationLayer()
    exported = layer.export_result(layer.build(_input()))

    assert "sleep_state" not in exported
    assert "wake_state" not in exported
