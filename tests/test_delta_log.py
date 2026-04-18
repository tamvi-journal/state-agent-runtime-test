from __future__ import annotations

from state.delta_log import DeltaRecord


def test_basic_no_big_change_event_stays_compact() -> None:
    event = DeltaRecord()

    assert event.mode_shift == ""
    assert event.coherence_shift == 0.0


def test_mode_change_is_surfaced() -> None:
    event = DeltaRecord(mode_shift="build->audit")

    assert event.mode_shift == "build->audit"


def test_repair_event_can_be_marked_explicitly() -> None:
    event = DeltaRecord(coherence_shift=0.2, repair_event=True)

    assert event.coherence_shift == 0.2
    assert event.repair_event is True


def test_policy_intrusion_is_a_compact_bool() -> None:
    event = DeltaRecord(policy_intrusion_detected=True)

    assert event.policy_intrusion_detected is True


def test_archive_consulted_remains_compact_bool() -> None:
    event = DeltaRecord(archive_consulted=True)

    assert event.archive_consulted is True


def test_no_transcript_dump_is_introduced() -> None:
    exported = DeltaRecord(trigger_cue="small posture update").to_dict()

    assert "transcript" not in exported


def test_no_sleep_logic_is_introduced() -> None:
    exported = DeltaRecord(trigger_cue="small posture update").to_dict()

    assert "sleep_state" not in exported
    assert "wake_state" not in exported
