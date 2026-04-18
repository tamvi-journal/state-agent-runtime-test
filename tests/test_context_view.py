from __future__ import annotations

from context.context_view import ContextViewBuilder
from state.live_state import LiveState
from verification.verification_record import VerificationRecord


def _state() -> LiveState:
    return LiveState(
        active_mode="build",
        current_axis="technical",
        coherence_level=0.9,
        tension_flags=[],
        active_project="thin-runtime-harness",
        user_signal="pytest",
        continuity_anchor="pytest-anchor",
        archive_needed=False,
    )


def test_basic_compact_build() -> None:
    builder = ContextViewBuilder()
    view = builder.build_pre_action(
        live_state=_state(),
        task_focus="add compact runtime canary",
        current_environment_state="local repository ready",
        open_obligations=["keep canary narrow"],
        current_risk="none",
    )

    assert view["active_project"] == "thin-runtime-harness"
    assert view["task_focus"] == "add compact runtime canary"


def test_verified_result_is_surfaced() -> None:
    builder = ContextViewBuilder()
    record = VerificationRecord(
        intended_action="run worker",
        executed_action="worker.run()",
        expected_change="payload exists",
        observed_outcome="payload exists",
        verification_status="passed",
    )
    view = builder.build_post_action(
        live_state=_state(),
        task_focus="inspect verification",
        current_environment_state="worker finished",
        verification_record=record,
        open_obligations=["synthesize"],
        current_risk="none",
        action_summary="worker returned evidence",
    )

    assert view["last_verified_result"]["observed_outcome"] == "payload exists"
    assert view["verification_status"] == "passed"


def test_open_obligations_are_preserved() -> None:
    builder = ContextViewBuilder()
    view = builder.build_pre_action(
        live_state=_state(),
        task_focus="keep scope narrow",
        current_environment_state="local repository ready",
        open_obligations=["keep scope narrow", "do not add archive routing"],
        current_risk="none",
    )

    assert view["open_obligations"] == ["keep scope narrow", "do not add archive routing"]


def test_output_stays_compact_and_not_transcript_like() -> None:
    builder = ContextViewBuilder()
    exported = builder.build_pre_action(
        live_state=_state(),
        task_focus="stay compact",
        current_environment_state="local repository ready",
        open_obligations=["keep state compact"],
        current_risk="none",
    )

    assert set(exported.keys()) == {
        "context_phase",
        "active_project",
        "active_mode",
        "current_axis",
        "task_focus",
        "current_environment_state",
        "last_verified_result",
        "open_obligations",
        "current_risk",
        "archive_needed",
        "continuity_anchor",
        "user_signal",
    }
    assert "transcript" not in exported
    assert "conversation_history" not in exported


def test_no_archive_driving_behavior_is_introduced() -> None:
    builder = ContextViewBuilder()
    exported = builder.build_pre_action(
        live_state=_state(),
        task_focus="stay local",
        current_environment_state="local repository ready",
        open_obligations=[],
        current_risk="none",
    )

    assert "archive_route" not in exported
    assert "archive_replay" not in exported


def test_no_sleep_logic_is_introduced() -> None:
    builder = ContextViewBuilder()
    exported = builder.build_pre_action(
        live_state=_state(),
        task_focus="stay local",
        current_environment_state="local repository ready",
        open_obligations=[],
        current_risk="none",
    )

    assert "sleep_state" not in exported
    assert "wake_state" not in exported
