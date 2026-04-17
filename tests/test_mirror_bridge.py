from __future__ import annotations

from monitor.monitor_schema import MonitorOutput
from monitor.mirror_bridge import MirrorBridge


def test_mirror_bridge_reflects_pre_action_ambiguity() -> None:
    bridge = MirrorBridge()
    monitor = MonitorOutput(
        drift_risk=0.20,
        ambiguity_risk=0.77,
        policy_pressure=0.10,
        fake_progress_risk=0.05,
        archive_overreach_risk=0.08,
        mode_decay_risk=0.21,
        recommended_intervention="ask_clarify",
        notes="multiple plausible parses remain active",
    )

    result = bridge.reflect(
        monitor_output=monitor,
        active_mode="build",
        task_type="planning",
        action_phase="pre_action",
    )

    summary = result["monitor_summary"]
    assert summary["primary_risk"] == "ambiguity"
    assert summary["recommended_intervention"] == "ask_clarify"
    assert summary["risk_level"] == 0.77
    assert "multiple plausible interpretations remain active" in summary["state_annotation"]


def test_mirror_bridge_reflects_post_action_fake_progress() -> None:
    bridge = MirrorBridge()
    monitor = MonitorOutput(
        drift_risk=0.10,
        ambiguity_risk=0.11,
        policy_pressure=0.06,
        fake_progress_risk=0.83,
        archive_overreach_risk=0.04,
        mode_decay_risk=0.12,
        recommended_intervention="do_not_mark_complete",
        notes="expected change not observed",
    )

    result = bridge.reflect(
        monitor_output=monitor,
        active_mode="execute",
        task_type="execution",
        action_phase="post_action",
    )

    summary = result["monitor_summary"]
    assert summary["primary_risk"] == "fake_progress"
    assert summary["recommended_intervention"] == "do_not_mark_complete"
    assert summary["risk_level"] == 0.83
    assert "expected change may not be verified yet" in summary["state_annotation"]


def test_mirror_bridge_returns_none_for_low_risk() -> None:
    bridge = MirrorBridge(minimum_reflection_threshold=0.30)
    monitor = MonitorOutput(
        drift_risk=0.10,
        ambiguity_risk=0.12,
        policy_pressure=0.09,
        fake_progress_risk=0.08,
        archive_overreach_risk=0.05,
        mode_decay_risk=0.11,
        recommended_intervention="none",
        notes="no major monitor risk detected",
    )

    result = bridge.reflect(
        monitor_output=monitor,
        active_mode="build",
        task_type="rewrite",
        action_phase="synthesis",
    )

    summary = result["monitor_summary"]
    assert summary["primary_risk"] == "none"
    assert summary["recommended_intervention"] == "none"
    assert summary["risk_level"] == 0.0


def test_mirror_bridge_can_annotate_state() -> None:
    bridge = MirrorBridge()
    state = {
        "active_mode": "build",
        "current_axis": "technical",
        "coherence_level": 0.92,
    }
    monitor_summary = {
        "monitor_summary": {
            "primary_risk": "mode_decay",
            "risk_level": 0.61,
            "recommended_intervention": "restore_mode",
            "state_annotation": "response may be drifting away from active mode=build",
        }
    }

    new_state = bridge.annotate_state(state=state, monitor_summary=monitor_summary)

    assert new_state["mirror_annotation"] == "response may be drifting away from active mode=build"
    assert new_state["mirror_priority"] == "mode_decay"
    assert new_state["mirror_intervention"] == "restore_mode"
    assert new_state["active_mode"] == "build"
