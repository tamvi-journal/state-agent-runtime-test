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


def test_monitor_flags_archive_overreach() -> None:
    monitor = MonitorLayer(archive_fragment_soft_limit=3)

    result = monitor.evaluate(
        context_view={"active_project": "state-memory-agent", "task_focus": "answer from current state"},
        live_state={"active_mode": "build"},
        delta_log={"policy_intrusion_detected": False, "repair_event": False},
        current_message="Continue the same thing.",
        draft_response="Here is the answer.",
        action_status={"verification_status": "none", "observed_outcome": ""},
        archive_status={"archive_consulted": True, "fragments_used": 6},
    )

    assert result.archive_overreach_risk > 0.30
    assert result.recommended_intervention in {"reduce_archive_weight", "ask_clarify", "tighten_project_focus"}


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
