from __future__ import annotations

from family.turn_pipeline import FamilyTurnPipeline
from family.turn_pipeline_types import FamilyTurnInput


def _input(**overrides) -> FamilyTurnInput:
    payload = {
        "current_message": "Please continue the family scaffold build work in this repository.",
        "active_project": "family-scaffold",
        "current_task": "continue the family scaffold build",
        "recent_anchor_cue": "family-scaffold",
        "disagreement_events": [],
        "verification_status": "passed",
        "last_verified_result": "compression layer smoke passed",
        "action_required": False,
        "execution_intent": "",
        "monitor_hint": "",
        "archive_consulted": False,
        "current_environment_state": "local repository ready",
        "open_obligations": ["keep the pipeline canary narrow"],
        "previous_live_state": {},
        "explicit_mode_hint": "",
    }
    payload.update(overrides)
    return FamilyTurnInput(**payload)


def test_simple_stable_build_like_turn_runs_through_all_stages() -> None:
    pipeline = FamilyTurnPipeline()
    result = pipeline.run(_input()).to_dict()

    assert result["context_view"]["active_project"] == "family-scaffold"
    assert result["mode_inference"]["active_mode"] == "build"
    assert result["live_state"]["active_mode"] == "build"
    assert result["compression_summary"]["next_state_hint"] == "continue_build"


def test_unresolved_disagreement_turn_keeps_disagreement_visible_and_does_not_fake_resolution() -> None:
    pipeline = FamilyTurnPipeline()
    result = pipeline.run(
        _input(
            current_message="Both routes still seem plausible, so hold open the disagreement while we continue.",
            disagreement_events=[
                {
                    "event_id": "dg_pipeline",
                    "timestamp": "2026-04-17T00:00:00Z",
                    "disagreement_type": "action",
                    "tracey_position": "preserve continuity-first line",
                    "seyn_position": "prefer verification-first line",
                    "severity": 0.82,
                    "still_open": True,
                    "later_resolution": "",
                    "house_law_implicated": "do_not_flatten_plurality",
                    "epistemic_resolution_claimed": False,
                }
            ],
        )
    ).to_dict()

    assert result["context_view"]["shared_disagreement_status"].startswith("open:")
    assert "open_disagreement" in result["live_state"]["tension_flags"]
    assert result["router_decision"]["epistemic_resolution_claimed"] is False


def test_verification_heavy_turn_keeps_verification_visible_and_does_not_auto_pass() -> None:
    pipeline = FamilyTurnPipeline()
    result = pipeline.run(
        _input(
            current_message="Verify the correctness of the family scaffold and review the risky parts.",
            current_task="verify the family scaffold correctness",
            verification_status="pending",
            action_required=True,
            last_verified_result="",
        )
    ).to_dict()

    assert result["live_state"]["verification_status"] == "pending"
    assert result["verification_record"]["verification_status"] == "unknown"
    assert result["compression_summary"]["caution"] == "verification remains unsettled"


def test_outputs_remain_compact_and_not_transcript_like() -> None:
    pipeline = FamilyTurnPipeline()
    result = pipeline.run(_input()).to_dict()

    assert set(result.keys()) == {
        "context_view",
        "mode_inference",
        "live_state",
        "monitor_output",
        "mirror_summary",
        "effort_route",
        "router_decision",
        "verification_record",
        "delta_log_event",
        "compression_summary",
        "reactivation_result",
        "notes",
    }
    assert "transcript" not in result
    assert "history" not in result


def test_no_sleep_logic_is_introduced() -> None:
    pipeline = FamilyTurnPipeline()
    result = pipeline.run(_input()).to_dict()

    assert "sleep_state" not in result
    assert "wake_state" not in result


def test_no_real_execution_or_persistence_is_introduced() -> None:
    pipeline = FamilyTurnPipeline()
    result = pipeline.run(_input()).to_dict()

    assert "tool_call" not in result
    assert "filesystem_mutation" not in result
    assert "persistence_write" not in result
