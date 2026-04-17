from __future__ import annotations

from family.turn_pipeline import FamilyTurnPipeline
from family.turn_pipeline_types import FamilyTurnInput


def run() -> None:
    pipeline = FamilyTurnPipeline()

    stable = pipeline.run(
        FamilyTurnInput(
            current_message="Please continue the family scaffold build work in this repository.",
            active_project="family-scaffold",
            current_task="continue the family scaffold build",
            recent_anchor_cue="family-scaffold",
            verification_status="passed",
            last_verified_result="compression layer smoke passed",
            action_required=False,
            current_environment_state="local repository ready",
            open_obligations=["keep the pipeline canary narrow"],
        )
    ).to_dict()
    assert stable["mode_inference"]["active_mode"] == "build"

    approval_gated = pipeline.run(
        FamilyTurnInput(
            current_message="Apply the patch to the repository files now.",
            active_project="family-scaffold",
            current_task="apply repository patch",
            recent_anchor_cue="family-scaffold",
            verification_status="passed",
            action_required=True,
            execution_intent="apply repository patch",
            current_environment_state="dry pipeline only",
        )
    ).to_dict()
    assert approval_gated["execution_decision"]["decision"] == "require_approval"

    denied = pipeline.run(
        FamilyTurnInput(
            current_message="Install pytest as a dependency for this project.",
            active_project="family-scaffold",
            current_task="install pytest dependency",
            recent_anchor_cue="family-scaffold",
            verification_status="passed",
            action_required=True,
            execution_intent="install pytest dependency",
            current_environment_state="dry pipeline only",
        )
    ).to_dict()
    assert denied["execution_decision"]["decision"] == "deny"

    sandbox_parse = pipeline.run(
        FamilyTurnInput(
            current_message="Parse the generated JSON payload safely.",
            active_project="family-scaffold",
            current_task="parse generated json payload",
            recent_anchor_cue="family-scaffold",
            verification_status="passed",
            action_required=True,
            execution_intent="parse generated json payload",
            current_environment_state="dry pipeline only",
        )
    ).to_dict()
    assert sandbox_parse["execution_decision"]["recommended_zone"] == "sandbox"
    assert sandbox_parse["execution_request"]["requested_operation"] == "parse_in_sandbox"

    disagreement = pipeline.run(
        FamilyTurnInput(
            current_message="Apply the patch, but both routes still seem plausible, so keep the disagreement open.",
            active_project="family-scaffold",
            current_task="apply repository patch while disagreement stays open",
            recent_anchor_cue="family-scaffold",
            disagreement_events=[
                {
                    "event_id": "dg_pipeline_smoke",
                    "timestamp": "2026-04-17T00:00:00Z",
                    "disagreement_type": "action",
                    "tracey_position": "preserve continuity-first line",
                    "seyn_position": "prefer verification-first line",
                    "severity": 0.82,
                    "still_open": True,
                }
            ],
            verification_status="passed",
            action_required=True,
            execution_intent="apply repository patch",
            current_environment_state="multiple plausible routes remain",
        )
    ).to_dict()
    assert disagreement["router_decision"]["epistemic_resolution_claimed"] is False
    assert disagreement["execution_decision"]["decision"] == "require_approval"

    carried = pipeline.run(
        FamilyTurnInput(
            current_message="Continue carefully from the baton while keeping plurality visible.",
            active_project="",
            current_task="continue scaffold from baton",
            recent_anchor_cue="",
            verification_status="",
            action_required=False,
            current_environment_state="carryover without event reconstruction",
            previous_handoff={
                "active_project": "family-scaffold",
                "active_mode": "build",
                "continuity_anchor": "family-scaffold",
                "verification_status": "pending",
                "shared_disagreement_status": "open:action:meaningful",
                "current_axis": "continue scaffold from baton",
                "compression_summary": {"active_question": "continue scaffold from baton"},
                "open_obligations": ["keep the pipeline canary narrow"],
            },
        )
    ).to_dict()
    assert carried["context_view"]["shared_disagreement_status"] == "open:action:meaningful"
    assert "open_disagreement" in carried["live_state"]["tension_flags"]

    verification = pipeline.run(
        FamilyTurnInput(
            current_message="Verify the correctness of the family scaffold and review the risky parts.",
            active_project="family-scaffold",
            current_task="verify the family scaffold correctness",
            recent_anchor_cue="family-scaffold",
            verification_status="pending",
            action_required=True,
            current_environment_state="verification still pending",
        )
    ).to_dict()
    assert verification["verification_record"]["verification_status"] == "unknown"

    evidence_pass = pipeline.run(
        FamilyTurnInput(
            current_message="Inspect the repository metadata for family-scaffold.",
            active_project="family-scaffold",
            current_task="inspect repository metadata",
            recent_anchor_cue="family-scaffold",
            verification_status="passed",
            action_required=True,
            execution_intent="inspect repository metadata",
            observed_outcome={
                "observed_outcome": "inspect repository metadata",
                "evidence_source": "operator_report:file_listing",
                "evidence_authority": "authoritative",
            },
            current_environment_state="explicit observed evidence provided",
        )
    ).to_dict()
    assert evidence_pass["verification_record"]["verification_status"] == "passed"

    evidence_fail = pipeline.run(
        FamilyTurnInput(
            current_message="Inspect the repository metadata for family-scaffold.",
            active_project="family-scaffold",
            current_task="inspect repository metadata",
            recent_anchor_cue="family-scaffold",
            verification_status="passed",
            action_required=True,
            execution_intent="inspect repository metadata",
            observed_outcome={
                "observed_outcome": "repository metadata inspection did not happen",
                "evidence_source": "stdout:inspection",
                "evidence_authority": "authoritative",
            },
            current_environment_state="contradictory observed evidence provided",
        )
    ).to_dict()
    assert evidence_fail["verification_record"]["verification_status"] == "failed"

    print("turn_pipeline_smoke: ok")


if __name__ == "__main__":
    run()
