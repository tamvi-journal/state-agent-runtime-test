from __future__ import annotations

from allocator.effort_allocator import EffortAllocator
from monitor.monitor_layer import MonitorLayer
from monitor.mirror_bridge import MirrorBridge
from runtime.governance_pass import GovernancePass


def build_governance_pass() -> GovernancePass:
    return GovernancePass(
        monitor_layer=MonitorLayer(),
        mirror_bridge=MirrorBridge(),
        effort_allocator=EffortAllocator(),
    )


def test_governance_pass_fake_progress_turn() -> None:
    gp = build_governance_pass()

    result = gp.run(
        context_view={
            "active_project": "state-memory-agent",
            "task_focus": "write file",
        },
        live_state={
            "active_mode": "execute",
            "current_axis": "technical",
            "coherence_level": 0.90,
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
        task_type="execution",
        domain="build/research",
        action_phase="post_action",
        mode_confidence=0.90,
        risk_score=0.65,
        stakes_signal=0.75,
        memory_commit_possible=False,
        disagreement_likelihood=0.10,
        cue_strength=0.20,
        high_risk_domain=False,
        unanswerable_likelihood=0.10,
    )

    assert result["monitor_output"]["fake_progress_risk"] >= 0.65
    assert result["monitor_summary"]["primary_risk"] == "fake_progress"
    assert result["monitor_summary"]["recommended_intervention"] == "do_not_mark_complete"
    assert result["annotated_state"]["mirror_priority"] == "fake_progress"
    assert result["effort_decision"]["verification_requirement"] == "mandatory"


def test_governance_pass_ambiguity_turn() -> None:
    gp = build_governance_pass()

    result = gp.run(
        context_view={
            "active_project": "state-memory-agent",
            "task_focus": "continue same unresolved thing",
        },
        live_state={
            "active_mode": "50_50",
            "current_axis": "exploratory",
            "coherence_level": 0.72,
        },
        delta_log={
            "policy_intrusion_detected": False,
            "repair_event": False,
        },
        current_message="Continue the same thing from before.",
        draft_response="I think we should do X.",
        action_status={
            "verification_status": "none",
            "observed_outcome": "",
        },
        archive_status={
            "archive_consulted": False,
            "fragments_used": 0,
        },
        task_type="planning",
        domain="build/research",
        action_phase="pre_action",
        mode_confidence=0.45,
        risk_score=0.30,
        stakes_signal=0.70,
        memory_commit_possible=True,
        disagreement_likelihood=0.65,
        cue_strength=0.15,
        high_risk_domain=False,
        unanswerable_likelihood=0.20,
    )

    assert result["monitor_output"]["ambiguity_risk"] >= 0.35
    assert result["monitor_summary"]["primary_risk"] == "ambiguity"
    assert result["monitor_summary"]["recommended_intervention"] == "ask_clarify"
    assert result["effort_decision"]["effort_level"] in {"medium", "high"}
    assert result["effort_decision"]["disagreement_handling"] in {
        "preserve_if_present",
        "actively_hold_open",
    }


def test_governance_pass_low_stakes_rewrite_turn() -> None:
    gp = build_governance_pass()

    result = gp.run(
        context_view={
            "active_project": "state-memory-agent",
            "task_focus": "light rewrite",
        },
        live_state={
            "active_mode": "build",
            "current_axis": "technical",
            "coherence_level": 0.95,
        },
        delta_log={
            "policy_intrusion_detected": False,
            "repair_event": False,
        },
        current_message="Rewrite this sentence more cleanly.",
        draft_response="Here is a cleaner version.",
        action_status={
            "verification_status": "none",
            "observed_outcome": "",
        },
        archive_status={
            "archive_consulted": False,
            "fragments_used": 0,
        },
        task_type="rewrite",
        domain="generic",
        action_phase="synthesis",
        mode_confidence=0.95,
        risk_score=0.05,
        stakes_signal=0.10,
        memory_commit_possible=False,
        disagreement_likelihood=0.05,
        cue_strength=0.90,
        high_risk_domain=False,
        unanswerable_likelihood=0.05,
    )

    assert result["monitor_summary"]["primary_risk"] in {"none", "drift", "mode_decay", "ambiguity"}
    assert result["effort_decision"]["effort_level"] == "low"
    assert result["effort_decision"]["cognition_topology"] == "single_brain"


def test_governance_pass_high_stakes_architecture_turn() -> None:
    gp = build_governance_pass()

    result = gp.run(
        context_view={
            "active_project": "state-memory-agent",
            "task_focus": "architecture decision for family scaffold",
        },
        live_state={
            "active_mode": "build",
            "current_axis": "technical",
            "coherence_level": 0.88,
        },
        delta_log={
            "policy_intrusion_detected": False,
            "repair_event": False,
        },
        current_message="Decide how the child memory system should be shaped.",
        draft_response="There are several possible structures still open.",
        action_status={
            "verification_status": "none",
            "observed_outcome": "",
        },
        archive_status={
            "archive_consulted": True,
            "fragments_used": 2,
        },
        task_type="architecture",
        domain="build/research",
        action_phase="synthesis",
        mode_confidence=0.55,
        risk_score=0.45,
        stakes_signal=0.95,
        memory_commit_possible=True,
        disagreement_likelihood=0.70,
        cue_strength=0.20,
        high_risk_domain=False,
        unanswerable_likelihood=0.30,
    )

    assert result["effort_decision"]["effort_level"] == "high"
    assert result["effort_decision"]["cognition_topology"] == "parallel_full"
    assert result["effort_decision"]["memory_commit_status"] == "allowed_after_verification"
