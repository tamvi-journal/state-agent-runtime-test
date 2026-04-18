from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shell.telegram_contract import TelegramInboundMessage, TelegramOutboundMessage
from transport.transport_contract import TransportInboundEnvelope, TransportOutboundEnvelope


@dataclass(slots=True)
class TelegramTransportMapper:
    """
    Transport-shaped mapping for Telegram.

    This is below the Telegram shell adapter and above any future webhook transport.
    """

    def inbound_to_envelope(
        self,
        *,
        inbound: TelegramInboundMessage | dict[str, Any],
    ) -> TransportInboundEnvelope:
        if isinstance(inbound, dict):
            inbound = TelegramInboundMessage(**inbound)

        return TransportInboundEnvelope(
            transport="telegram",
            transport_message_id=inbound.message_id,
            session_id=f"telegram:{inbound.chat_id}",
            source_user_id=inbound.user_id,
            payload=inbound.to_dict(),
        )

    def outbound_from_shell_payload(
        self,
        *,
        inbound: TelegramInboundMessage | dict[str, Any],
        outbound_message: TelegramOutboundMessage | dict[str, Any],
    ) -> TransportOutboundEnvelope:
        if isinstance(inbound, dict):
            inbound = TelegramInboundMessage(**inbound)
        if isinstance(outbound_message, dict):
            outbound_message = TelegramOutboundMessage(**outbound_message)

        return TransportOutboundEnvelope(
            transport="telegram",
            destination_id=inbound.chat_id,
            payload=outbound_message.to_dict(),
            reply_to_transport_message_id=inbound.message_id,
        )
