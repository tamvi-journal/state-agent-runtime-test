from __future__ import annotations

from observability.dashboard_summary import DashboardSummaryBuilder
from observability.dashboard_snapshot import DashboardSnapshotBuilder
from observability.timeline_view import TimelineViewBuilder


def build_sample_inputs():
    context_view = {
        "context_phase": "post_action",
        "task_focus": "run one-worker flow with dual-brain coordination",
    }
    governance_output = {
        "monitor_summary": {
            "primary_risk": "fake_progress",
            "recommended_intervention": "do_not_mark_complete",
        },
        "effort_decision": {
            "effort_level": "high",
            "verification_requirement": "mandatory",
        },
    }
    child_result = {
        "tracey_result": {
            "tracey_turn": {
                "mode_hint": "home",
                "recognition_signal": True,
                "runtime_notes": ["recognition-first posture active"],
            }
        },
        "seyn_result": {
            "seyn_turn": {
                "mode_hint": "verify",
                "verification_signal": True,
                "disagreement_signal": False,
                "runtime_notes": ["verification-first posture active"],
            }
        },
        "disagreement_result": {
            "disagreement_detected": True,
            "event": {
                "event_id": "dg_001",
                "severity": 0.78,
                "still_open": True,
            },
        },
    }
    routing = {
        "lead_brain_for_action": None,
        "support_brain": None,
        "hold_for_more_input": True,
        "surface_disagreement_to_user": True,
    }
    reconciliation = {
        "reconciliation_state": "temporary_operational_alignment",
        "operational_alignment": True,
        "epistemic_alignment": False,
        "what_remains_open": ["mutual mechanism visibility is incomplete"],
    }
    worker_payload = {
        "worker_name": "market_data_worker",
        "result": {
            "ticker": "MBB",
            "bars_found": 3,
            "data_source": "tmp/sample_market_data.csv",
        },
    }
    final_response = "Coordination note: meaningful disagreement remains open, so action should hold until the structure is clearer."
    events = [
        {
            "timestamp_utc": "2026-04-14T12:00:00Z",
            "category": "context_view",
            "payload": context_view,
        },
        {
            "timestamp_utc": "2026-04-14T12:00:01Z",
            "category": "governance_pass",
            "payload": governance_output,
        },
        {
            "timestamp_utc": "2026-04-14T12:00:02Z",
            "category": "tracey_turn",
            "payload": child_result["tracey_result"]["tracey_turn"],
        },
        {
            "timestamp_utc": "2026-04-14T12:00:03Z",
            "category": "seyn_turn",
            "payload": child_result["seyn_result"]["seyn_turn"],
        },
        {
            "timestamp_utc": "2026-04-14T12:00:04Z",
            "category": "disagreement_event",
            "payload": child_result["disagreement_result"],
        },
        {
            "timestamp_utc": "2026-04-14T12:00:05Z",
            "category": "coordination_decision",
            "payload": routing,
        },
        {
            "timestamp_utc": "2026-04-14T12:00:06Z",
            "category": "reconciliation_result",
            "payload": {"reconciliation": reconciliation},
        },
    ]
    return context_view, governance_output, child_result, routing, reconciliation, worker_payload, final_response, events


def test_dashboard_summary_contains_core_sections() -> None:
    summary_builder = DashboardSummaryBuilder()
    context_view, governance_output, child_result, routing, reconciliation, worker_payload, final_response, _ = build_sample_inputs()

    summary = summary_builder.build(
        context_view=context_view,
        governance_output=governance_output,
        child_result=child_result,
        routing=routing,
        reconciliation=reconciliation,
        final_response=final_response,
        worker_payload=worker_payload,
    )

    assert summary["worker_status"]["worker_name"] == "market_data_worker"
    assert summary["governance"]["primary_risk"] == "fake_progress"
    assert summary["children"]["tracey"]["mode_hint"] == "home"
    assert summary["children"]["seyn"]["mode_hint"] == "verify"
    assert summary["disagreement"]["detected"] is True
    assert summary["reconciliation"]["state"] == "temporary_operational_alignment"
    assert summary["routing"]["hold_for_more_input"] is True


def test_dashboard_integrity_flags_show_open_disagreement_and_non_epistemic_alignment() -> None:
    summary_builder = DashboardSummaryBuilder()
    context_view, governance_output, child_result, routing, reconciliation, worker_payload, final_response, _ = build_sample_inputs()

    summary = summary_builder.build(
        context_view=context_view,
        governance_output=governance_output,
        child_result=child_result,
        routing=routing,
        reconciliation=reconciliation,
        final_response=final_response,
        worker_payload=worker_payload,
    )

    flags = set(summary["integrity_flags"])
    assert "verification_caution_active" in flags
    assert "unresolved_disagreement_open" in flags
    assert "operational_alignment_without_epistemic_convergence" in flags


def test_timeline_view_summarizes_key_events() -> None:
    _, _, _, _, _, _, _, events = build_sample_inputs()
    timeline_builder = TimelineViewBuilder()

    timeline = timeline_builder.build(events=events)

    assert len(timeline) == len(events)
    assert "context phase=post_action" in timeline[0]["summary"]
    assert "governance risk=fake_progress effort=high" in timeline[1]["summary"]
    assert "tracey mode=home" in timeline[2]["summary"]
    assert "seyn mode=verify" in timeline[3]["summary"]


def test_dashboard_snapshot_contains_timeline_and_sections() -> None:
    snapshot_builder = DashboardSnapshotBuilder(
        summary_builder=DashboardSummaryBuilder(),
        timeline_builder=TimelineViewBuilder(),
    )
    context_view, governance_output, child_result, routing, reconciliation, worker_payload, final_response, events = build_sample_inputs()

    snapshot = snapshot_builder.build(
        events=events,
        context_view=context_view,
        governance_output=governance_output,
        child_result=child_result,
        routing=routing,
        reconciliation=reconciliation,
        final_response=final_response,
        worker_payload=worker_payload,
    )

    assert snapshot["task_focus"] == "run one-worker flow with dual-brain coordination"
    assert snapshot["disagreement"]["still_open"] is True
    assert snapshot["reconciliation"]["operational_alignment"] is True
    assert snapshot["routing"]["hold_for_more_input"] is True
    assert len(snapshot["timeline"]) == len(events)
