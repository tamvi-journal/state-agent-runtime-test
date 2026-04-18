from __future__ import annotations

from handoff.handoff_builder import HandoffBuilder


def test_handoff_builder_returns_only_the_compact_baton_fields() -> None:
    baton = HandoffBuilder().build(
        task_focus="verify bounded market-data lookup for MBB",
        active_mode="build",
        verification_status="passed",
        monitor_summary={
            "primary_risk": "none",
            "risk_level": 0.0,
            "recommended_intervention": "none",
            "state_annotation": "no major monitor risk visible",
        },
        next_hint="decide whether another bounded lookup is needed",
    ).to_dict()

    assert set(baton.keys()) == {
        "task_focus",
        "active_mode",
        "open_loops",
        "verification_status",
        "monitor_summary",
        "next_hint",
    }


def test_handoff_keeps_open_verification_visible() -> None:
    baton = HandoffBuilder().build(
        task_focus="verify bounded market-data lookup for VCB",
        active_mode="build",
        verification_status="unknown",
        monitor_summary={
            "primary_risk": "fake_progress",
            "risk_level": 0.7,
            "recommended_intervention": "do_not_mark_complete",
            "state_annotation": "expected change may not be verified yet",
        },
        next_hint="inspect the worker result before treating the task as complete",
    )

    assert "verification remains open" in baton.open_loops
    assert "monitor:fake_progress" in baton.open_loops
