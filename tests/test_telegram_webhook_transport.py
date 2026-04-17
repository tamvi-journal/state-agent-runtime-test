from __future__ import annotations

from transport.telegram_webhook_bridge import TelegramWebhookBridge
from transport.telegram_webhook_parser import TelegramWebhookParser
from transport.telegram_webhook_response import build_webhook_response


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


def build_webhook_payload(text: str = "hello there") -> dict:
    return {
        "update_id": 10001,
        "message": {
            "message_id": 501,
            "text": text,
            "chat": {"id": 777},
            "from": {
                "id": 42,
                "username": "ty_user",
                "first_name": "Ty",
            },
        },
    }


def test_parser_reads_minimal_webhook_payload() -> None:
    parser = TelegramWebhookParser()
    update = parser.parse(build_webhook_payload("inspect run"))

    assert update.chat_id == "777"
    assert update.user_id == "42"
    assert update.message_id == "501"
    assert update.text == "inspect run"


def test_webhook_bridge_routes_payload_into_transport_layer() -> None:
    bridge = TelegramWebhookBridge()
    result = bridge.handle_webhook(
        webhook_payload=build_webhook_payload("/builder inspect run"),
        runtime_result=build_runtime_result(),
    )

    assert result["parsed_update"]["chat_id"] == "777"
    transport_result = result["transport_result"]
    assert transport_result["ack"] is not None
    assert transport_result["transport_outbound"] is not None
    assert transport_result["shell_request"]["requested_mode"] == "builder"


def test_webhook_response_builder_accepts_successful_transport_result() -> None:
    bridge = TelegramWebhookBridge()
    result = bridge.handle_webhook(
        webhook_payload=build_webhook_payload("hello there"),
        runtime_result=build_runtime_result(),
    )

    response = build_webhook_response(
        transport_result=result["transport_result"],
    )

    assert response.accepted is True
    assert response.status == "accepted"
    assert response.outbound_message is not None


def test_webhook_parser_rejects_non_text_message() -> None:
    parser = TelegramWebhookParser()

    bad_payload = {
        "update_id": 10002,
        "message": {
            "message_id": 502,
            "chat": {"id": 777},
            "from": {"id": 42},
        },
    }

    try:
        parser.parse(bad_payload)
    except ValueError as e:
        assert "missing text" in str(e)
    else:
        raise AssertionError("Expected ValueError for missing text")
