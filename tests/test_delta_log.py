from __future__ import annotations

from family.delta_log import DeltaLogBuilder
from family.delta_log_types import DeltaLogInput


def _state(**overrides) -> dict[str, object]:
    payload = {
        "active_mode": "build",
        "current_axis": "add delta-log canary",
        "coherence_level": "stable",
        "tension_flags": [],
        "policy_pressure": "low",
        "active_project": "family-scaffold",
        "continuity_anchor": "family-scaffold",
        "user_signal": "add delta-log canary",
        "archive_needed": False,
        "verification_status": "passed",
    }
    payload.update(overrides)
    return payload


def _input(**overrides) -> DeltaLogInput:
    payload = {
        "previous_live_state": _state(),
        "current_live_state": _state(),
        "recent_trigger_cue": "small posture update",
        "archive_consulted": False,
        "verification_before": "",
        "verification_after": "",
    }
    payload.update(overrides)
    return DeltaLogInput(**payload)


def test_basic_no_big_change_event_stays_compact() -> None:
    builder = DeltaLogBuilder()
    event = builder.build(_input())

    assert event.mode_shift == "none"
    assert event.coherence_shift == "flat"


def test_mode_change_is_surfaced() -> None:
    builder = DeltaLogBuilder()
    event = builder.build(
        _input(
            current_live_state=_state(active_mode="audit"),
        )
    )

    assert event.mode_shift == "build->audit"


def test_coherence_improvement_can_mark_repair_event() -> None:
    builder = DeltaLogBuilder()
    event = builder.build(
        _input(
            previous_live_state=_state(coherence_level="strained", tension_flags=["verification_unsettled"]),
            current_live_state=_state(coherence_level="stable", tension_flags=[]),
        )
    )

    assert event.coherence_shift == "up"
    assert event.repair_event is True


def test_unresolved_ambiguity_can_remain_visible() -> None:
    builder = DeltaLogBuilder()
    event = builder.build(
        _input(
            current_live_state=_state(
                active_mode="50_50",
                coherence_level="strained",
                tension_flags=["open_disagreement"],
            )
        )
    )

    assert event.ambiguity_unresolved is True


def test_verification_change_is_surfaced() -> None:
    builder = DeltaLogBuilder()
    event = builder.build(
        _input(
            previous_live_state=_state(verification_status="pending"),
            current_live_state=_state(verification_status="passed"),
        )
    )

    assert event.verification_changed == "pending->passed"


def test_archive_consulted_remains_compact_bool() -> None:
    builder = DeltaLogBuilder()
    event = builder.build(_input(archive_consulted=True))

    assert event.archive_consulted is True


def test_no_transcript_dump_is_introduced() -> None:
    builder = DeltaLogBuilder()
    exported = builder.export_event(builder.build(_input()))

    assert "previous_live_state" not in exported
    assert "current_live_state" not in exported
    assert "transcript" not in exported


def test_no_sleep_logic_is_introduced() -> None:
    builder = DeltaLogBuilder()
    exported = builder.export_event(builder.build(_input()))

    assert "sleep_state" not in exported
    assert "wake_state" not in exported
