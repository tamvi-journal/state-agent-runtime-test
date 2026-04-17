from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from transport.telegram_webhook_contract import TelegramWebhookUpdate


@dataclass(slots=True)
class TelegramWebhookParser:
    """
    Parse a Telegram-like webhook payload into a minimal internal update object.

    This parser is deliberately strict and only accepts text-message style updates.
    """

    def parse(self, payload: dict[str, Any]) -> TelegramWebhookUpdate:
        message = payload.get("message")
        if not isinstance(message, dict):
            raise ValueError("webhook payload missing message")

        chat = message.get("chat", {})
        from_user = message.get("from", {})
        text = message.get("text", "")

        if not str(text).strip():
            raise ValueError("webhook payload missing text")

        return TelegramWebhookUpdate(
            update_id=str(payload.get("update_id", "")),
            chat_id=str(chat.get("id", "")),
            user_id=str(from_user.get("id", "")),
            message_id=str(message.get("message_id", "")),
            text=str(text),
            username=str(from_user.get("username", "")),
            first_name=str(from_user.get("first_name", "")),
        )
