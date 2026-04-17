from __future__ import annotations

from shell.operator_console_bridge import OperatorConsoleBridge
from shell.operator_console_renderer import OperatorConsoleRenderer
from shell.operator_console_runtime import OperatorConsoleRuntime


def build_sample_inputs():
    runtime_result = {
        "final_response": "Coordination note: meaningful disagreement remains open, so action should hold until the structure is clearer.",
        "routing": {
            "lead_brain_for_action": None,
            "support_brain": None,
            "hold_for_more_input": True,
            "surface_disagreement_to_user": True,
        },
        "reconciliation": {
            "reconciliation_state": "temporary_operational_alignment",
            "operational_alignment": True,
            "epistemic_alignment": False,
            "what_remains_open": ["mutual mechanism visibility is incomplete"],
        },
        "child_result": {
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
        },
    }
    context_view = {
        "context_phase": "post_action",
        "task_focus": "run dual-brain coordinated worker flow",
    }
    governance_output = {
        "monitor_summary": {
            "primary_risk": "fake_progress",
            "recommended_intervention": "do_not_mark_complete",
        },
        "effort_decision": {
            "effort_level": "high",
            "verification_requirement": "mandatory",
            "monitor_intensity": "strict",
            "disagreement_handling": "actively_hold_open",
        },
    }
    worker_payload = {
        "worker_name": "market_data_worker",
        "result": {
            "ticker": "MBB",
            "bars_found": 3,
            "data_source": "tmp/sample_market_data.csv",
        },
    }
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
            "payload": runtime_result["child_result"]["tracey_result"]["tracey_turn"],
        },
        {
            "timestamp_utc": "2026-04-14T12:00:03Z",
            "category": "seyn_turn",
            "payload": runtime_result["child_result"]["seyn_result"]["seyn_turn"],
        },
        {
            "timestamp_utc": "2026-04-14T12:00:04Z",
            "category": "disagreement_event",
            "payload": runtime_result["child_result"]["disagreement_result"],
        },
        {
            "timestamp_utc": "2026-04-14T12:00:05Z",
            "category": "reconciliation_result",
            "payload": {"reconciliation": runtime_result["reconciliation"]},
        },
    ]
    return runtime_result, events, context_view, governance_output, worker_payload


def test_operator_console_bridge_builds_sections() -> None:
    runtime_result, events, context_view, governance_output, worker_payload = build_sample_inputs()
    bridge = OperatorConsoleBridge()

    payload = bridge.build(
        runtime_result=runtime_result,
        events=events,
        context_view=context_view,
        governance_output=governance_output,
        worker_payload=worker_payload,
    )

    assert payload["operator_snapshot"]["hold_for_more_input"] is True
    assert payload["dashboard_snapshot"]["disagreement"]["detected"] is True
    assert len(payload["console_sections"]) == 4


def test_operator_console_renderer_outputs_compact_text() -> None:
    runtime_result, events, context_view, governance_output, worker_payload = build_sample_inputs()
    bridge = OperatorConsoleBridge()
    renderer = OperatorConsoleRenderer()

    payload = bridge.build(
        runtime_result=runtime_result,
        events=events,
        context_view=context_view,
        governance_output=governance_output,
        worker_payload=worker_payload,
    )
    rendered = renderer.render(console_payload=payload)

    assert "[operator-console]" in rendered
    assert "reconciliation_state=temporary_operational_alignment" in rendered
    assert "flags=" in rendered


def test_operator_console_runtime_runs_end_to_end() -> None:
    runtime_result, events, context_view, governance_output, worker_payload = build_sample_inputs()
    runtime = OperatorConsoleRuntime()

    result = runtime.run(
        runtime_result=runtime_result,
        events=events,
        context_view=context_view,
        governance_output=governance_output,
        worker_payload=worker_payload,
    )

    assert "console_payload" in result
    assert "rendered_text" in result
    assert "hold=True" in result["rendered_text"]
