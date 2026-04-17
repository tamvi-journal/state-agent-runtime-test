from __future__ import annotations

from family.compression_layer import CompressionLayer
from family.compression_types import CompressionInput


def run() -> None:
    layer = CompressionLayer()

    stable = layer.build(
        CompressionInput(
            context_view={
                "active_project": "family-scaffold",
                "active_mode": "build",
                "task_focus": "stabilize the family scaffold",
                "verification_status": "passed",
            },
            live_state={
                "active_mode": "build",
                "coherence_level": "stable",
                "tension_flags": [],
                "active_project": "family-scaffold",
                "continuity_anchor": "family-scaffold",
                "verification_status": "passed",
            },
            delta_log_event={"mode_shift": "none"},
            recent_anchor_cue="family-scaffold",
            verification_status="passed",
        )
    )
    assert stable.next_state_hint == "continue_build"

    verification = layer.build(
        CompressionInput(
            context_view={
                "active_project": "family-scaffold",
                "active_mode": "audit",
                "task_focus": "verify recent canary output",
                "verification_status": "pending",
            },
            live_state={
                "active_mode": "audit",
                "coherence_level": "strained",
                "tension_flags": ["verification_unsettled"],
                "active_project": "family-scaffold",
                "continuity_anchor": "verify-output",
                "verification_status": "pending",
            },
            delta_log_event={"verification_changed": "none"},
            recent_anchor_cue="verify-output",
            verification_status="pending",
        )
    )
    assert verification.caution == "verification remains unsettled"

    disagreement = layer.build(
        CompressionInput(
            context_view={
                "active_project": "family-scaffold",
                "active_mode": "50_50",
                "task_focus": "hold open the disagreement",
                "verification_status": "passed",
            },
            live_state={
                "active_mode": "50_50",
                "coherence_level": "strained",
                "tension_flags": ["open_disagreement"],
                "active_project": "family-scaffold",
                "continuity_anchor": "hold-open",
                "verification_status": "passed",
            },
            delta_log_event={"mode_shift": "build->50_50"},
            recent_anchor_cue="hold-open",
            verification_status="passed",
            disagreement_open=True,
        )
    )
    assert disagreement.caution == "meaningful disagreement remains open"

    print("compression_layer_smoke: ok")


if __name__ == "__main__":
    run()
