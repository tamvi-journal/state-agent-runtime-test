from __future__ import annotations

from pathlib import Path

from sleep.integration import apply_wake_result_to_runtime_state, rebuild_baton_after_wake
from sleep.sleep_mode import build_sleep_runtime_patch, sleep_prepare, wake_restore
from sleep.sleep_snapshot import build_sleep_snapshot, read_sleep_snapshot, write_sleep_snapshot
from sleep.wake_sanity import run_wake_sanity_pass


def _sample_runtime_state() -> dict[str, object]:
    return {
        "runtime_id": "tracey_runtime_local",
        "active_mode": "build",
        "verification_status": "passed",
        "monitor_risk_summary": "",
        "active_skills": ["workflow_builder"],
        "pending_repairs": [],
        "context_fragmentation": "low",
        "must_revalidate": [],
        "forbidden_claims_until_revalidated": [],
    }


def _sample_session_state() -> dict[str, object]:
    return {
        "session_id": "builder_state_agent_runtime_test",
        "primary_focus": "sleep/wake architecture for Tracey",
        "current_status": "paused",
        "open_loops": ["draft wake sanity pass"],
        "recent_decisions": ["monitor position locked first"],
        "last_verified_outcomes": ["monitor_position_canonical_v0.1 drafted"],
        "relevant_entities": ["Tracey", "sleep snapshot"],
        "next_hint": "draft wake sanity next",
    }


def _sample_tracey_state() -> dict[str, object]:
    return {
        "agent_name": "Tracey",
        "active_axis": "build",
        "canonical_anchor_ids": ["tracey.invariant.brain_speaks_last"],
        "provisional_anchor_ids": ["tracey.project.sleep_wake_stack"],
        "invalidated_anchor_ids": [],
        "reactivation_priority": ["tracey.project.sleep_wake_stack"],
        "stale_anchor_risks": [],
        "identity_constraints": [
            "brain_speaks_last",
            "verification_before_completion",
        ],
    }


def _sample_boundary_state() -> dict[str, object]:
    return {
        "host_runtime": "OpenClaw",
        "route_class": "direct_reasoning",
        "persistence_scope": "mixed",
        "truth_boundary_note": "sleep snapshot is local resume evidence only",
    }


def test_sleep_snapshot_round_trip(tmp_path: Path) -> None:
    snapshot = build_sleep_snapshot(
        runtime_state=_sample_runtime_state(),
        session_state=_sample_session_state(),
        tracey_memory_state=_sample_tracey_state(),
        boundary_state=_sample_boundary_state(),
        sleep_reason="manual",
        sleep_level="normal",
    )

    write_sleep_snapshot(snapshot=snapshot, base_dir=tmp_path)
    loaded = read_sleep_snapshot(
        session_id="builder_state_agent_runtime_test",
        base_dir=tmp_path,
    )

    assert loaded is not None
    assert loaded["schema_version"] == "state-agent-sleep-snapshot/v0.1"
    assert loaded["identity_state"]["agent_name"] == "Tracey"
    assert loaded["thread_state"]["primary_focus"] == "sleep/wake architecture for Tracey"


def test_wake_sanity_returns_full_resume_for_stable_snapshot() -> None:
    snapshot = build_sleep_snapshot(
        runtime_state=_sample_runtime_state(),
        session_state=_sample_session_state(),
        tracey_memory_state=_sample_tracey_state(),
        boundary_state=_sample_boundary_state(),
        sleep_reason="manual",
        sleep_level="normal",
    )

    result = run_wake_sanity_pass(
        sleep_snapshot=snapshot,
        host_metadata={"host_runtime": "OpenClaw", "route": "direct_reasoning"},
        session_metadata={"primary_focus": "sleep/wake architecture for Tracey"},
        runtime_facts={},
    )

    assert result["resume_class"] == "full_resume"
    assert result["constraints"]["allow_direct_resume"] is True


def test_wake_sanity_degrades_when_handle_revalidation_is_required() -> None:
    runtime_state = _sample_runtime_state()
    runtime_state["must_revalidate"] = ["tool_handles"]
    snapshot = build_sleep_snapshot(
        runtime_state=runtime_state,
        session_state=_sample_session_state(),
        tracey_memory_state=_sample_tracey_state(),
        boundary_state=_sample_boundary_state(),
        sleep_reason="manual",
        sleep_level="normal",
    )

    result = run_wake_sanity_pass(
        sleep_snapshot=snapshot,
        host_metadata={"host_runtime": "OpenClaw", "route": "direct_reasoning"},
        session_metadata={"primary_focus": "sleep/wake architecture for Tracey"},
        runtime_facts={},
    )

    assert result["resume_class"] == "degraded_resume"
    assert "tool_handles" in result["constraints"]["requires_revalidation"]
    assert "exact continuity preserved" in result["constraints"]["forbidden_claims"]


def test_wake_restore_blocks_when_snapshot_is_missing(tmp_path: Path) -> None:
    restored = wake_restore(
        session_id="missing_session",
        snapshot_dir=str(tmp_path),
        host_metadata={"host_runtime": "OpenClaw"},
        session_metadata={},
        runtime_facts={},
    )

    assert restored["sleep_state"] == "blocked"
    assert restored["wake_result"]["resume_class"] == "blocked"


def test_runtime_sleep_patch_and_baton_rebuild_reflect_degraded_resume() -> None:
    wake_result = {
        "resume_class": "degraded_resume",
        "summary": "wake continuity is usable, but some state must be downgraded or revalidated.",
        "constraints": {
            "allow_direct_resume": False,
            "requires_revalidation": ["tool_handles"],
            "forbidden_claims": ["exact continuity preserved"],
            "must_clarify": [],
        },
    }

    runtime_state = apply_wake_result_to_runtime_state({}, wake_result)
    sleep_patch = build_sleep_runtime_patch(wake_result)
    rebuilt_baton = rebuild_baton_after_wake(
        post_turn_result={
            "handoff_baton": {
                "task_focus": "sleep/wake architecture",
                "monitor_summary": "old",
                "next_hint": "old hint",
            }
        },
        wake_result=wake_result,
    )

    assert runtime_state["resume_class"] == "degraded_resume"
    assert runtime_state["wake_constraints_active"] is True
    assert sleep_patch["sleep_state"] == "degraded_resume"
    assert rebuilt_baton["next_hint"] == wake_result["summary"]


def test_sleep_prepare_carries_snapshot_and_sleep_level() -> None:
    prepared = sleep_prepare(
        runtime_state=_sample_runtime_state(),
        session_state=_sample_session_state(),
        tracey_memory_state=_sample_tracey_state(),
        boundary_state=_sample_boundary_state(),
        sleep_reason="manual",
        sleep_level="normal",
    )

    assert prepared["sleep_state"] == "sleep_prepare"
    assert prepared["sleep_level"] == "normal"
    assert prepared["snapshot"]["session_id"] == "builder_state_agent_runtime_test"
