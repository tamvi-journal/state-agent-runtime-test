from __future__ import annotations

from family.reactivation_layer import ReactivationLayer
from family.reactivation_types import ReactivationInput


def run() -> None:
    layer = ReactivationLayer()

    strong = layer.build(
        ReactivationInput(
            current_message="Please continue the family-scaffold build work now.",
            detected_cues=["family-scaffold", "build"],
            active_project_hint="family-scaffold",
            compression_summary={
                "anchor_cue": "family-scaffold",
                "next_state_hint": "continue_build",
            },
            context_view={"active_project": "family-scaffold", "active_mode": "build"},
            live_state={"active_mode": "build", "current_axis": "continue build", "coherence_level": "stable", "active_project": "family-scaffold"},
            recent_anchor_cue="family-scaffold",
            verification_status="passed",
        )
    )
    assert strong.reactivation_triggered is True

    lower = layer.build(
        ReactivationInput(
            current_message="Please continue family-scaffold, but verification is still pending.",
            detected_cues=["family-scaffold"],
            active_project_hint="family-scaffold",
            compression_summary={
                "anchor_cue": "family-scaffold",
                "next_state_hint": "verify",
            },
            context_view={"active_project": "family-scaffold", "active_mode": "audit"},
            live_state={"active_mode": "audit", "current_axis": "verify-first", "coherence_level": "strained", "active_project": "family-scaffold"},
            recent_anchor_cue="family-scaffold",
            disagreement_open=True,
            verification_status="pending",
        )
    )
    assert lower.confidence < strong.confidence

    weak = layer.build(
        ReactivationInput(
            current_message="Hello there.",
            detected_cues=[],
            active_project_hint="",
            compression_summary={"anchor_cue": "", "next_state_hint": ""},
            context_view={},
            live_state={"active_mode": "", "current_axis": "", "coherence_level": "mixed", "active_project": ""},
            recent_anchor_cue="",
            verification_status="passed",
        )
    )
    assert weak.reactivation_triggered is False or weak.confidence < 0.50

    print("reactivation_layer_smoke: ok")


if __name__ == "__main__":
    run()
