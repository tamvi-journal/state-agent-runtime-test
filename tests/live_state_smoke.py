from __future__ import annotations

from family.live_state import LiveStateBuilder
from family.live_state_types import LiveStateInput


def run() -> None:
    builder = LiveStateBuilder()

    stable = builder.build(
        LiveStateInput(
            context_view={
                "active_project": "family-scaffold",
                "active_mode": "build",
                "task_focus": "stabilize the family canary layer",
                "open_obligations": ["keep scope narrow"],
                "verification_status": "passed",
                "shared_disagreement_status": "none",
            },
            mode_inference_result={
                "active_mode": "build",
                "confidence": 0.86,
                "secondary_mode": "",
                "reasons": ["mode cues favored build"],
            },
            verification_status="passed",
            active_project="family-scaffold",
            recent_anchor_cue="family-scaffold",
        )
    )
    assert stable.coherence_level == "stable"

    verification_tension = builder.build(
        LiveStateInput(
            context_view={
                "active_project": "family-scaffold",
                "active_mode": "audit",
                "task_focus": "verify recent behavior",
                "open_obligations": ["do not over-claim"],
                "verification_status": "pending",
                "shared_disagreement_status": "none",
            },
            mode_inference_result={
                "active_mode": "audit",
                "confidence": 0.72,
                "secondary_mode": "",
                "reasons": ["mode cues favored audit"],
            },
            verification_status="pending",
            active_project="family-scaffold",
            monitor_summary={"primary_risk": "fake_progress", "risk_level": 0.74},
        )
    )
    assert "verification_unsettled" in verification_tension.tension_flags

    disagreement = builder.build(
        LiveStateInput(
            context_view={
                "active_project": "family-scaffold",
                "active_mode": "50_50",
                "task_focus": "choose next step under disagreement",
                "open_obligations": ["preserve plurality"],
                "verification_status": "passed",
                "shared_disagreement_status": "open:action:meaningful",
            },
            mode_inference_result={
                "active_mode": "50_50",
                "confidence": 0.42,
                "secondary_mode": "build",
                "reasons": ["ambiguity is meaningful enough to keep a dual-reading posture visible"],
            },
            verification_status="passed",
            active_project="family-scaffold",
            disagreement_open=True,
        )
    )
    assert "open_disagreement" in disagreement.tension_flags

    print("live_state_smoke: ok")


if __name__ == "__main__":
    run()
