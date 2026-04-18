from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shell.telegram_contract import TelegramInboundMessage
from transport.telegram_transport_mapper import TelegramTransportMapper
from transport.telegram_webhook_parser import TelegramWebhookParser
from transport.transport_bridge import TransportBridge


@dataclass(slots=True)
class TelegramWebhookBridge:
    """
    Webhook boundary for Telegram transport.

    Flow:
    webhook payload -> parsed Telegram update -> transport envelope -> transport bridge

    No HTTP server is implemented here.
    This is the pure boundary object that a future webhook handler can call.
    """

    parser: TelegramWebhookParser = field(default_factory=TelegramWebhookParser)
    mapper: TelegramTransportMapper = field(default_factory=TelegramTransportMapper)
    transport_bridge: TransportBridge = field(default_factory=TransportBridge)

    def handle_webhook(
        self,
        *,
        webhook_payload: dict[str, Any],
        runtime_result: dict[str, Any],
    ) -> dict[str, Any]:
        update = self.parser.parse(webhook_payload)

        inbound = TelegramInboundMessage(
            chat_id=update.chat_id,
            user_id=update.user_id,
            message_id=update.message_id,
            text=update.text,
            username=update.username,
            first_name=update.first_name,
        )

        envelope = self.mapper.inbound_to_envelope(inbound=inbound)
        bridge_result = self.transport_bridge.handle(
            inbound_envelope=envelope,
            runtime_result=runtime_result,
        )

        return {
            "parsed_update": update.to_dict(),
            "transport_result": bridge_result,
        }
