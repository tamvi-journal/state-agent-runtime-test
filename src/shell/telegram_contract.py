from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class TelegramInboundMessage:
    chat_id: str
    user_id: str
    message_id: str
    text: str
    username: str = ""
    first_name: str = ""

    def __post_init__(self) -> None:
        if not self.chat_id.strip():
            raise ValueError("chat_id must be non-empty")
        if not self.user_id.strip():
            raise ValueError("user_id must be non-empty")
        if not self.message_id.strip():
            raise ValueError("message_id must be non-empty")
        if not self.text.strip():
            raise ValueError("text must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TelegramOutboundMessage:
    chat_id: str
    text: str
    reply_to_message_id: str | None = None
    parse_mode: str | None = None
    disable_web_page_preview: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
