from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class TelegramWebhookUpdate:
    """
    Minimal Telegram webhook-shaped update.

    This is intentionally smaller than the full Telegram update schema.
    It only models the fields the current runtime needs.
    """

    update_id: str
    chat_id: str
    user_id: str
    message_id: str
    text: str
    username: str = ""
    first_name: str = ""

    def __post_init__(self) -> None:
        for field_name in ("update_id", "chat_id", "user_id", "message_id", "text"):
            value = getattr(self, field_name)
            if not str(value).strip():
                raise ValueError(f"{field_name} must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
