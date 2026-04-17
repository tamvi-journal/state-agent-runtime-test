from __future__ import annotations

from shell.operator_console_session import OperatorConsoleSession
from shell.shell_contract import ShellRequest
from shell.shell_response_formatter import ShellResponseFormatter
from shell.shell_runtime_bridge import ShellRuntimeBridge


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


def test_shell_runtime_bridge_returns_operator_snapshot_for_operator_channel() -> None:
    bridge = ShellRuntimeBridge()

    result = bridge.handle(
        shell_request=ShellRequest(
            channel="operator",
            user_text="inspect current run",
            user_id="op1",
            session_id="sess1",
            requested_mode="operator",
        ),
        runtime_result=build_runtime_result(),
    )

    assert result["shell_response"]["render_mode"] == "operator"
    assert result["operator_snapshot"] is not None
    assert result["operator_snapshot"]["reconciliation_state"] == "temporary_operational_alignment"


def test_shell_runtime_bridge_keeps_user_channel_clean() -> None:
    bridge = ShellRuntimeBridge()

    result = bridge.handle(
        shell_request=ShellRequest(
            channel="chat",
            user_text="hello",
            user_id="u1",
            session_id="sess1",
        ),
        runtime_result=build_runtime_result(),
    )

    assert result["shell_response"]["render_mode"] == "user"
    assert result["shell_response"]["trace_allowed"] is False
    assert result["operator_snapshot"] is None


def test_operator_console_session_tracks_latest_snapshot() -> None:
    session = OperatorConsoleSession(session_id="ops1")
    session.append(
        {
            "lead_brain_for_action": None,
            "support_brain": None,
            "hold_for_more_input": True,
            "reconciliation_state": "temporary_operational_alignment",
        }
    )

    latest = session.latest()
    summary = session.summary()

    assert latest is not None
    assert summary["items"] == 1
    assert summary["latest_hold_for_more_input"] is True


def test_shell_response_formatter_distinguishes_operator_surface() -> None:
    bridge = ShellRuntimeBridge()
    formatter = ShellResponseFormatter()

    payload = bridge.handle(
        shell_request=ShellRequest(
            channel="operator",
            user_text="inspect current run",
            user_id="op1",
            session_id="sess1",
            requested_mode="operator",
        ),
        runtime_result=build_runtime_result(),
    )

    formatted = formatter.format(shell_payload=payload)

    assert "Coordination note:" in formatted["surface_text"]
    assert "[operator]" in formatted["operator_text"]
