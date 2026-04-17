from __future__ import annotations

from shell.telegram_contract import TelegramInboundMessage
from transport.telegram_transport_mapper import TelegramTransportMapper
from transport.transport_bridge import TransportBridge
from transport.transport_contract import TransportInboundEnvelope
from transport.transport_policy import TransportPolicy


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


def test_transport_policy_for_telegram_requires_ack_and_allows_retry() -> None:
    policy = TransportPolicy().decide(transport="telegram")

    assert policy.ack_required is True
    assert policy.retry_allowed is True
    assert policy.operator_visible_failure is True


def test_telegram_mapper_converts_inbound_to_transport_envelope() -> None:
    mapper = TelegramTransportMapper()
    envelope = mapper.inbound_to_envelope(
        inbound=TelegramInboundMessage(
            chat_id="c1",
            user_id="u1",
            message_id="m1",
            text="hello",
        )
    )

    assert envelope.transport == "telegram"
    assert envelope.session_id == "telegram:c1"
    assert envelope.payload["text"] == "hello"


def test_transport_bridge_handles_telegram_envelope_end_to_end() -> None:
    bridge = TransportBridge()
    mapper = TelegramTransportMapper()

    inbound = mapper.inbound_to_envelope(
        inbound=TelegramInboundMessage(
            chat_id="c1",
            user_id="u1",
            message_id="m1",
            text="/builder inspect run",
        )
    )

    result = bridge.handle(
        inbound_envelope=inbound,
        runtime_result=build_runtime_result(),
    )

    assert result["ack"] is not None
    assert result["error"] is None
    assert result["transport_outbound"] is not None
    assert result["shell_request"]["requested_mode"] == "builder"


def test_transport_bridge_returns_error_for_unsupported_transport() -> None:
    bridge = TransportBridge()

    result = bridge.handle(
        inbound_envelope=TransportInboundEnvelope(
            transport="http",
            transport_message_id="h1",
            session_id="http:s1",
            source_user_id="u1",
            payload={"text": "hello"},
        ),
        runtime_result=build_runtime_result(),
    )

    assert result["ack"] is None
    assert result["error"] is not None
    assert result["error"]["status"] == "fatal_error"
