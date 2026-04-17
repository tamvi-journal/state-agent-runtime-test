from __future__ import annotations

from shell.telegram_adapter import TelegramAdapter
from shell.telegram_contract import TelegramInboundMessage
from shell.telegram_runtime_adapter import TelegramRuntimeAdapter


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


def test_inbound_to_shell_request_defaults_to_user_mode() -> None:
    adapter = TelegramAdapter()
    shell_request = adapter.inbound_to_shell_request(
        inbound=TelegramInboundMessage(
            chat_id="c1",
            user_id="u1",
            message_id="m1",
            text="hello there",
        )
    )

    assert shell_request.channel == "telegram"
    assert shell_request.requested_mode == "user"
    assert shell_request.user_text == "hello there"


def test_builder_prefix_switches_builder_view() -> None:
    adapter = TelegramAdapter()
    shell_request = adapter.inbound_to_shell_request(
        inbound=TelegramInboundMessage(
            chat_id="c1",
            user_id="u1",
            message_id="m1",
            text="/builder inspect current flow",
        )
    )

    assert shell_request.requested_mode == "builder"
    assert shell_request.wants_builder_view is True
    assert shell_request.user_text == "inspect current flow"


def test_runtime_adapter_returns_telegram_outbound() -> None:
    adapter = TelegramRuntimeAdapter()
    result = adapter.handle(
        inbound=TelegramInboundMessage(
            chat_id="c1",
            user_id="u1",
            message_id="m1",
            text="hello there",
        ),
        runtime_result=build_runtime_result(),
    )

    outbound = result["telegram_outbound"]
    assert outbound["chat_id"] == "c1"
    assert outbound["reply_to_message_id"] == "m1"
    assert "Coordination note:" in outbound["text"]


def test_builder_mode_is_reflected_in_outbound_prefix() -> None:
    adapter = TelegramRuntimeAdapter()
    result = adapter.handle(
        inbound=TelegramInboundMessage(
            chat_id="c1",
            user_id="u1",
            message_id="m1",
            text="/builder show runtime truth",
        ),
        runtime_result=build_runtime_result(),
    )

    outbound = result["telegram_outbound"]
    assert outbound["text"].startswith("[builder]")
