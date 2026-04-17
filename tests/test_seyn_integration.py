from __future__ import annotations

from runtime.seyn_runtime_pass import SeynRuntimePass
from seyn.seyn_adapter import SeynAdapter
from seyn.seyn_runtime_profile import build_seyn_runtime_profile


def test_seyn_adapter_detects_verify_mode_and_adds_verification_note() -> None:
    profile = build_seyn_runtime_profile()
    adapter = SeynAdapter(profile=profile)

    turn = adapter.inspect_turn(
        user_text="Please verify whether this is actually done.",
        context_view={"task_focus": "verify completion"},
        monitor_summary={"recommended_intervention": "none"},
    )

    assert turn["mode_hint"] == "verify"
    assert turn["verification_signal"] is True

    adapted = adapter.adapt_response(
        base_response="I read the turn.",
        seyn_turn=turn,
    )
    assert "Verification note: structural verification posture is active." in adapted


def test_seyn_adapter_keeps_false_completion_note_from_monitor() -> None:
    profile = build_seyn_runtime_profile()
    adapter = SeynAdapter(profile=profile)

    turn = adapter.inspect_turn(
        user_text="Is it done?",
        context_view={"task_focus": "completion check"},
        monitor_summary={"recommended_intervention": "do_not_mark_complete"},
    )

    assert "require evidence and observed outcome before completion" in turn["runtime_notes"]


def test_seyn_runtime_pass_patches_state() -> None:
    profile = build_seyn_runtime_profile()
    adapter = SeynAdapter(profile=profile)
    runtime_pass = SeynRuntimePass(adapter=adapter)

    result = runtime_pass.run(
        user_text="Please verify whether this is actually done.",
        context_view={"task_focus": "verify completion"},
        current_state={"active_mode": "build"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "none"},
    )

    assert result["state_patch"]["seyn_mode_hint"] == "verify"
    assert result["state_patch"]["seyn_verification_signal"] is True
    assert "Verification note: structural verification posture is active." in result["adapted_response"]


def test_seyn_runtime_pass_preserves_disagreement_signal() -> None:
    profile = build_seyn_runtime_profile()
    adapter = SeynAdapter(profile=profile)
    runtime_pass = SeynRuntimePass(adapter=adapter)

    result = runtime_pass.run(
        user_text="There is unresolved disagreement and tension here.",
        context_view={"task_focus": "preserve plurality"},
        current_state={"active_mode": "audit"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "ask_clarify"},
    )

    assert result["state_patch"]["seyn_disagreement_signal"] is True
    assert result["seyn_turn"]["monitor_intervention"] == "ask_clarify"
