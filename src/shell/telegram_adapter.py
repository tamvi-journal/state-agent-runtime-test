from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shell.shell_contract import ShellRequest
from shell.telegram_contract import TelegramInboundMessage, TelegramOutboundMessage


@dataclass(slots=True)
class TelegramAdapter:
    """
    Channel adapter between Telegram-shaped input/output and the generic shell contract.

    This adapter does not call Telegram APIs.
    It only converts payloads cleanly.
    """

    default_requested_mode: str = "user"
    allow_builder_prefix: bool = True

    def inbound_to_shell_request(
        self,
        *,
        inbound: TelegramInboundMessage | dict[str, Any],
        session_id: str | None = None,
    ) -> ShellRequest:
        if isinstance(inbound, dict):
            inbound = TelegramInboundMessage(**inbound)

        requested_mode = self.default_requested_mode
        wants_trace = False
        wants_builder_view = False
        normalized_text = inbound.text.strip()

        if self.allow_builder_prefix and normalized_text.startswith("/builder "):
            requested_mode = "builder"
            wants_builder_view = True
            normalized_text = normalized_text[len("/builder "):].strip()

        if normalized_text.startswith("/trace "):
            wants_trace = True
            normalized_text = normalized_text[len("/trace "):].strip()

        return ShellRequest(
            channel="telegram",
            user_text=normalized_text,
            user_id=inbound.user_id,
            session_id=session_id or f"telegram:{inbound.chat_id}",
            requested_mode=requested_mode,
            wants_trace=wants_trace,
            wants_builder_view=wants_builder_view,
        )

    def shell_payload_to_outbound(
        self,
        *,
        inbound: TelegramInboundMessage | dict[str, Any],
        shell_payload: dict[str, Any],
    ) -> TelegramOutboundMessage:
        if isinstance(inbound, dict):
            inbound = TelegramInboundMessage(**inbound)

        shell_response = shell_payload.get("shell_response", {})
        visible_text = str(shell_response.get("visible_response", "")).strip()
        render_mode = str(shell_response.get("render_mode", "user"))

        text = visible_text
        if render_mode == "builder":
            text = "[builder]\n" + text
        elif render_mode == "operator":
            text = "[operator]\n" + text

        return TelegramOutboundMessage(
            chat_id=inbound.chat_id,
            text=text,
            reply_to_message_id=inbound.message_id,
            parse_mode=None,
            disable_web_page_preview=True,
        )
