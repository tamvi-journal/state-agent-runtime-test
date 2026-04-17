from __future__ import annotations

from family.compression_layer import CompressionLayer
from family.compression_types import CompressionInput


def _input(**overrides) -> CompressionInput:
    payload = {
        "context_view": {
            "active_project": "family-scaffold",
            "active_mode": "build",
            "task_focus": "add compression canary",
            "verification_status": "passed",
            "shared_disagreement_status": "none",
        },
        "live_state": {
            "active_mode": "build",
            "current_axis": "add compression canary",
            "coherence_level": "stable",
            "tension_flags": [],
            "policy_pressure": "low",
            "active_project": "family-scaffold",
            "continuity_anchor": "family-scaffold",
            "user_signal": "add compression canary",
            "archive_needed": False,
            "verification_status": "passed",
        },
        "delta_log_event": {
            "mode_shift": "none",
            "coherence_shift": "flat",
            "policy_intrusion_detected": False,
            "repair_event": False,
            "ambiguity_unresolved": False,
            "trigger_cue": "small posture update",
            "archive_consulted": False,
            "verification_changed": "none",
            "notes": [],
        },
        "recent_anchor_cue": "family-scaffold",
        "verification_status": "passed",
        "disagreement_open": False,
        "current_question": "",
        "task_focus": "",
    }
    payload.update(overrides)
    return CompressionInput(**payload)


def test_basic_compact_compression_summary_builds_cleanly() -> None:
    layer = CompressionLayer()
    summary = layer.build(_input())

    assert summary.active_question == "add compression canary"
    assert summary.anchor_cue == "family-scaffold"


def test_unresolved_verification_can_surface_caution() -> None:
    layer = CompressionLayer()
    summary = layer.build(
        _input(
            verification_status="pending",
            live_state={
                "active_mode": "audit",
                "current_axis": "verify recent output",
                "coherence_level": "strained",
                "tension_flags": ["verification_unsettled"],
                "policy_pressure": "medium",
                "active_project": "family-scaffold",
                "continuity_anchor": "verify-output",
                "user_signal": "verify recent output",
                "archive_needed": False,
                "verification_status": "pending",
            },
        )
    )

    assert summary.caution == "verification remains unsettled"


def test_open_disagreement_can_surface_caution_without_bloat() -> None:
    layer = CompressionLayer()
    summary = layer.build(
        _input(
            disagreement_open=True,
            live_state={
                "active_mode": "50_50",
                "current_axis": "hold plurality",
                "coherence_level": "strained",
                "tension_flags": ["open_disagreement"],
                "policy_pressure": "low",
                "active_project": "family-scaffold",
                "continuity_anchor": "hold-plurality",
                "user_signal": "hold plurality",
                "archive_needed": False,
                "verification_status": "passed",
            },
        )
    )

    assert summary.caution == "meaningful disagreement remains open"
    assert len(summary.main_points) <= 3


def test_anchor_cue_remains_compact() -> None:
    layer = CompressionLayer()
    summary = layer.build(
        _input(
            recent_anchor_cue="compact-anchor-cue",
        )
    )

    assert summary.anchor_cue == "compact-anchor-cue"
    assert len(summary.anchor_cue) <= 64


def test_main_points_remain_small_and_non_transcript_like() -> None:
    layer = CompressionLayer()
    exported = layer.export_summary(layer.build(_input()))

    assert len(exported["main_points"]) <= 3
    assert "transcript" not in exported
    assert "conversation_history" not in exported


def test_no_archive_routing_is_introduced() -> None:
    layer = CompressionLayer()
    exported = layer.export_summary(layer.build(_input()))

    assert "archive_route" not in exported
    assert "archive_replay" not in exported


def test_no_sleep_logic_is_introduced() -> None:
    layer = CompressionLayer()
    exported = layer.export_summary(layer.build(_input()))

    assert "sleep_state" not in exported
    assert "wake_state" not in exported
