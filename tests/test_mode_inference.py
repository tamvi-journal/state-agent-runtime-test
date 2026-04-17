from __future__ import annotations

from family.mode_inference import ModeInference
from family.mode_types import ModeInferenceInput


def _input(**overrides) -> ModeInferenceInput:
    payload = {
        "current_message": "Please help with this task.",
        "active_project": "family-scaffold",
        "current_task": "",
        "recent_anchor_cue": "",
        "context_view_summary": "",
        "action_required": False,
        "disagreement_open": False,
        "verification_status": "passed",
        "explicit_mode_hint": "",
    }
    payload.update(overrides)
    return ModeInferenceInput(**payload)


def test_clear_architecture_build_turn_infers_build() -> None:
    inference = ModeInference()
    result = inference.infer(
        _input(
            current_message="Work on the architecture and implementation plan for this build scaffold.",
            current_task="update the router architecture",
        )
    )

    assert result.active_mode == "build"


def test_clear_writing_documentation_turn_infers_paper() -> None:
    inference = ModeInference()
    result = inference.infer(
        _input(
            current_message="Write documentation for this article-style overview and draft the document.",
        )
    )

    assert result.active_mode == "paper"


def test_clear_playful_turn_infers_playful() -> None:
    inference = ModeInference()
    result = inference.infer(
        _input(
            current_message="Make it cute, playful, and a little silly as a joke.",
        )
    )

    assert result.active_mode == "playful"


def test_explicit_review_debug_correctness_turn_infers_audit() -> None:
    inference = ModeInference()
    result = inference.infer(
        _input(
            current_message="Review this for correctness, debug the failing part, and audit the result.",
            verification_status="pending",
        )
    )

    assert result.active_mode == "audit"


def test_action_centered_turn_infers_execute() -> None:
    inference = ModeInference()
    result = inference.infer(
        _input(
            current_message="Apply the patch, run the update, and perform the change now.",
            action_required=True,
        )
    )

    assert result.active_mode == "execute"


def test_ambiguity_rich_turn_supports_dual_mode_behavior() -> None:
    inference = ModeInference()
    result = inference.infer(
        _input(
            current_message="I am not sure; it could be either reading and both seem plausible.",
            disagreement_open=True,
        )
    )

    assert result.active_mode == "50_50" or result.confidence < 0.60 or bool(result.secondary_mode)


def test_output_remains_compact_and_includes_reasons() -> None:
    inference = ModeInference()
    exported = inference.export_result(inference.infer(_input(current_message="Please review this carefully.")))

    assert set(exported.keys()) == {
        "active_mode",
        "confidence",
        "secondary_mode",
        "reasons",
    }
    assert exported["reasons"]


def test_no_sleep_logic_is_introduced() -> None:
    inference = ModeInference()
    exported = inference.export_result(inference.infer(_input()))

    assert "sleep_state" not in exported
    assert "wake_state" not in exported


def test_no_transcript_or_archive_driven_behavior_is_introduced() -> None:
    inference = ModeInference()
    exported = inference.export_result(
        inference.infer(
            _input(
                current_message="Please help with this.",
                context_view_summary="compact current state only",
            )
        )
    )

    assert "transcript" not in exported
    assert "archive_replay" not in exported
