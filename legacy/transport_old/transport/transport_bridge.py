from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shell.telegram_contract import TelegramInboundMessage
from shell.telegram_runtime_adapter import TelegramRuntimeAdapter
from transport.telegram_transport_mapper import TelegramTransportMapper
from transport.transport_contract import (
    TransportAck,
    TransportError,
    TransportInboundEnvelope,
    TransportOutboundEnvelope,
)
from transport.transport_policy import TransportPolicy


@dataclass(slots=True)
class TransportBridge:
    """
    Unified bridge:
    transport envelope -> channel adapter -> shell/runtime -> transport envelope
    """

    transport_policy: TransportPolicy = field(default_factory=TransportPolicy)
    telegram_runtime_adapter: TelegramRuntimeAdapter = field(default_factory=TelegramRuntimeAdapter)
    telegram_transport_mapper: TelegramTransportMapper = field(default_factory=TelegramTransportMapper)

    def handle(
        self,
        *,
        inbound_envelope: TransportInboundEnvelope | dict[str, Any],
        runtime_result: dict[str, Any],
    ) -> dict[str, Any]:
        if isinstance(inbound_envelope, dict):
            inbound_envelope = TransportInboundEnvelope(**inbound_envelope)

        policy = self.transport_policy.decide(transport=inbound_envelope.transport)

        if inbound_envelope.transport == "telegram":
            inbound = TelegramInboundMessage(**inbound_envelope.payload)
            adapted = self.telegram_runtime_adapter.handle(
                inbound=inbound,
                runtime_result=runtime_result,
            )
            outbound = self.telegram_transport_mapper.outbound_from_shell_payload(
                inbound=inbound,
                outbound_message=adapted["telegram_outbound"],
            )
            ack = TransportAck(
                transport="telegram",
                status="ack",
                reason="telegram envelope was normalized and adapted successfully",
                transport_message_id=inbound_envelope.transport_message_id,
            )
            return {
                "policy": policy.to_dict(),
                "shell_request": adapted["shell_request"],
                "shell_payload": adapted["shell_payload"],
                "transport_outbound": outbound.to_dict(),
                "ack": ack.to_dict(),
                "error": None,
            }

        error = TransportError(
            transport=inbound_envelope.transport,
            status="fatal_error",
            reason="unsupported transport for current bridge",
            retryable=False,
            transport_message_id=inbound_envelope.transport_message_id,
        )
        return {
            "policy": policy.to_dict(),
            "shell_request": None,
            "shell_payload": None,
            "transport_outbound": None,
            "ack": None,
            "error": error.to_dict(),
        }
