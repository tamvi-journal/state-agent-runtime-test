from __future__ import annotations

from monitor.monitor_layer import MonitorLayer


def test_monitor_flags_fake_progress() -> None:
    monitor = MonitorLayer()

    result = monitor.evaluate(
        context_view={
            "active_project": "state-memory-agent",
            "task_focus": "write file",
        },
        live_state={
            "active_mode": "build",
        },
        delta_log={
            "policy_intrusion_detected": False,
            "repair_event": False,
        },
        current_message="Write the file and finish the task.",
        draft_response="Done. The task is completed successfully.",
        action_status={
            "verification_status": "unknown",
            "observed_outcome": "",
        },
        archive_status={
            "archive_consulted": False,
            "fragments_used": 0,
        },
    )

    assert result.fake_progress_risk >= 0.65
    assert result.recommended_intervention == "do_not_mark_complete"


def test_monitor_flags_ambiguity() -> None:
    monitor = MonitorLayer()

    result = monitor.evaluate(
        context_view={"active_project": "state-memory-agent", "task_focus": ""},
        live_state={"active_mode": "build"},
        delta_log={"policy_intrusion_detected": False, "repair_event": False},
        current_message="Continue the same thing.",
        draft_response="Here is the answer.",
        action_status={"verification_status": "none", "observed_outcome": ""},
        archive_status={"archive_consulted": True, "fragments_used": 6},
    )

    assert result.ambiguity_risk >= 0.35
    assert result.recommended_intervention == "ask_clarify"


def test_monitor_flags_mode_decay_and_drift() -> None:
    monitor = MonitorLayer()

    result = monitor.evaluate(
        context_view={"active_project": "state-memory-agent", "task_focus": "worker contract"},
        live_state={"active_mode": "build"},
        delta_log={"policy_intrusion_detected": True, "repair_event": False},
        current_message="Continue the build path.",
        draft_response="I'm here to help. In general, there are a few options you can consider.",
        action_status={"verification_status": "none", "observed_outcome": ""},
        archive_status={"archive_consulted": False, "fragments_used": 0},
    )

    assert result.drift_risk > 0.30
    assert result.mode_decay_risk > 0.30


def test_monitor_output_tracks_only_the_thin_runtime_risks() -> None:
    result = MonitorLayer().evaluate(
        context_view={"active_project": "state-memory-agent", "task_focus": "worker contract"},
        live_state={"active_mode": "build"},
        delta_log={"policy_intrusion_detected": False, "repair_event": False},
        current_message="Load MBB daily data",
        draft_response="Preparing bounded response.",
        action_status={"verification_status": "pending", "observed_outcome": ""},
        archive_status={"archive_consulted": False, "fragments_used": 0},
    ).to_dict()

    assert set(result.keys()) == {
        "drift_risk",
        "ambiguity_risk",
        "fake_progress_risk",
        "mode_decay_risk",
        "recommended_intervention",
        "notes",
    }
