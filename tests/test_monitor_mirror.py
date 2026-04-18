from __future__ import annotations

from monitor.mirror_bridge import MirrorBridge
from monitor.monitor_layer import MonitorLayer


def test_pre_action_ambiguity_case_compresses_to_ambiguity() -> None:
    monitor = MonitorLayer()
    bridge = MirrorBridge()

    output = monitor.evaluate(
        context_view={"active_project": "thin-runtime-harness", "task_focus": ""},
        live_state={"active_mode": "build"},
        delta_log={"policy_intrusion_detected": False, "repair_event": False},
        current_message="Continue that.",
        draft_response="We should continue.",
        action_status={"verification_status": "pending", "observed_outcome": ""},
        archive_status={"archive_consulted": False, "fragments_used": 0},
    )
    summary = bridge.reflect(
        monitor_output=output,
        active_mode="build",
        task_type="architecture",
        action_phase="pre_action",
    )["monitor_summary"]

    assert summary["primary_risk"] == "ambiguity"


def test_post_action_fake_progress_case_compresses_to_fake_progress() -> None:
    monitor = MonitorLayer()
    bridge = MirrorBridge()

    output = monitor.evaluate(
        context_view={"active_project": "thin-runtime-harness", "task_focus": "apply change"},
        live_state={"active_mode": "build"},
        delta_log={"policy_intrusion_detected": False, "repair_event": False},
        current_message="Apply the change.",
        draft_response="Done successfully.",
        action_status={"verification_status": "pending", "observed_outcome": ""},
        archive_status={"archive_consulted": False, "fragments_used": 0},
    )
    summary = bridge.reflect(
        monitor_output=output,
        active_mode="build",
        task_type="execution",
        action_phase="post_action",
    )["monitor_summary"]

    assert summary["primary_risk"] == "fake_progress"


def test_mode_decay_case_recommends_restore_mode() -> None:
    monitor = MonitorLayer()

    output = monitor.evaluate(
        context_view={"active_project": "thin-runtime-harness", "task_focus": "schema work"},
        live_state={"active_mode": "build"},
        delta_log={"policy_intrusion_detected": False, "repair_event": False},
        current_message="Continue the build path.",
        draft_response="This feels warm and gentle and caring.",
        action_status={"verification_status": "pending", "observed_outcome": ""},
        archive_status={"archive_consulted": False, "fragments_used": 0},
    )

    assert output.recommended_intervention == "restore_mode"


def test_mirror_summary_remains_compact_and_excludes_full_monitor_object() -> None:
    monitor = MonitorLayer()
    bridge = MirrorBridge()

    output = monitor.evaluate(
        context_view={"active_project": "thin-runtime-harness", "task_focus": ""},
        live_state={"active_mode": "build"},
        delta_log={"policy_intrusion_detected": False, "repair_event": False},
        current_message="Continue that.",
        draft_response="We should continue.",
        action_status={"verification_status": "pending", "observed_outcome": ""},
        archive_status={"archive_consulted": False, "fragments_used": 0},
    )
    summary = bridge.reflect(
        monitor_output=output,
        active_mode="build",
        task_type="architecture",
        action_phase="pre_action",
    )["monitor_summary"]

    assert set(summary.keys()) == {
        "primary_risk",
        "risk_level",
        "recommended_intervention",
        "state_annotation",
    }
    assert "drift_risk" not in summary
    assert "notes" not in summary


def test_no_sleep_lifecycle_logic_is_introduced() -> None:
    monitor = MonitorLayer()
    output = monitor.evaluate(
        context_view={"active_project": "thin-runtime-harness", "task_focus": "schema"},
        live_state={"active_mode": "build"},
        delta_log={"policy_intrusion_detected": False, "repair_event": False},
        current_message="schema work only",
        draft_response="schema work only",
        action_status={"verification_status": "pending", "observed_outcome": ""},
        archive_status={"archive_consulted": False, "fragments_used": 0},
    ).to_dict()

    assert "sleep_state" not in output
    assert "wake_state" not in output


def test_monitor_canary_does_not_expand_into_router_authority() -> None:
    monitor = MonitorLayer()
    output = monitor.evaluate(
        context_view={"active_project": "thin-runtime-harness", "task_focus": "apply"},
        live_state={"active_mode": "build"},
        delta_log={"policy_intrusion_detected": False, "repair_event": False},
        current_message="Apply it.",
        draft_response="Done successfully.",
        action_status={"verification_status": "pending", "observed_outcome": ""},
        archive_status={"archive_consulted": False, "fragments_used": 0},
    ).to_dict()

    assert "router_decision" not in output
    assert "action_lead" not in output
