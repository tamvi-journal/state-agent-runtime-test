from __future__ import annotations

from shell.external_shell import ExternalShell
from shell.operator_snapshot import OperatorSnapshotBuilder
from shell.shell_contract import ShellRequest


def build_runtime_result() -> dict:
    return {
        "final_response": "Coordination note: meaningful disagreement remains open, so action should hold until the structure is clearer.",
        "routing": {
            "lead_brain_for_action": None,
            "support_brain": None,
            "hold_for_more_input": True,
            "surface_disagreement_to_user": True,
        },
        "reconciliation": {
            "reconciliation_state": "temporary_operational_alignment",
            "operational_alignment": True,
            "epistemic_alignment": False,
        },
        "child_result": {
            "disagreement_result": {
                "disagreement_detected": True,
                "event": {"event_id": "dg_001", "still_open": True},
            },
            "tracey_result": {
                "tracey_turn": {"mode_hint": "home", "recognition_signal": True}
            },
            "seyn_result": {
                "seyn_turn": {"mode_hint": "verify", "verification_signal": True}
            },
        },
    }


def test_user_shell_hides_trace_by_default() -> None:
    shell = ExternalShell()
    result = shell.handle(
        shell_request=ShellRequest(
            channel="chat",
            user_text="hi",
            user_id="u1",
            session_id="s1",
        ),
        runtime_result=build_runtime_result(),
    )

    assert result.render_mode == "user"
    assert result.trace_allowed is False
    assert result.trace_payload is None
    assert result.operator_payload is None


def test_debug_console_can_expose_trace() -> None:
    shell = ExternalShell()
    result = shell.handle(
        shell_request=ShellRequest(
            channel="debug_console",
            user_text="show trace",
            user_id="u1",
            session_id="s1",
            requested_mode="builder",
            wants_trace=True,
            wants_builder_view=True,
        ),
        runtime_result=build_runtime_result(),
    )

    assert result.render_mode == "builder"
    assert result.trace_allowed is True
    assert result.trace_payload is not None


def test_operator_channel_gets_operator_payload() -> None:
    shell = ExternalShell()
    result = shell.handle(
        shell_request=ShellRequest(
            channel="operator",
            user_text="inspect run",
            user_id="op1",
            session_id="ops1",
            requested_mode="operator",
        ),
        runtime_result=build_runtime_result(),
    )

    assert result.render_mode == "operator"
    assert result.trace_allowed is True
    assert result.operator_payload is not None
    assert "routing" in result.operator_payload


def test_operator_snapshot_reads_runtime_state() -> None:
    builder = OperatorSnapshotBuilder()
    snapshot = builder.build(runtime_result=build_runtime_result())

    assert snapshot["hold_for_more_input"] is True
    assert snapshot["disagreement_detected"] is True
    assert snapshot["reconciliation_state"] == "temporary_operational_alignment"
