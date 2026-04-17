from __future__ import annotations

from family.mode_inference import ModeInference
from family.mode_types import ModeInferenceInput


def run() -> None:
    inference = ModeInference()

    build = inference.infer(
        ModeInferenceInput(
            current_message="Work on the architecture and implementation details for this build task.",
            active_project="family-scaffold",
            current_task="build the next family canary",
        )
    )
    assert build.active_mode == "build"

    execute = inference.infer(
        ModeInferenceInput(
            current_message="Apply the patch and run the update now.",
            active_project="family-scaffold",
            current_task="ship the narrow canary",
            action_required=True,
        )
    )
    assert execute.active_mode == "execute"

    ambiguity = inference.infer(
        ModeInferenceInput(
            current_message="I am not sure, both readings still feel plausible.",
            active_project="family-scaffold",
            disagreement_open=True,
        )
    )
    assert ambiguity.active_mode == "50_50" or ambiguity.secondary_mode != ""

    audit = inference.infer(
        ModeInferenceInput(
            current_message="Review this for correctness and debug the failing part.",
            active_project="family-scaffold",
            verification_status="pending",
        )
    )
    assert audit.active_mode == "audit"

    print("mode_inference_smoke: ok")


if __name__ == "__main__":
    run()
