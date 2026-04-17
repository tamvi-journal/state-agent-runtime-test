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

    disagreement = pipeline.run(
        FamilyTurnInput(
            current_message="Both routes still seem plausible, so keep the disagreement open while we continue.",
            active_project="family-scaffold",
            current_task="hold open the current disagreement",
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
            action_required=False,
            current_environment_state="multiple plausible routes remain",
        )
    ).to_dict()
    assert disagreement["router_decision"]["epistemic_resolution_claimed"] is False

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

    print("turn_pipeline_smoke: ok")


if __name__ == "__main__":
    run()
