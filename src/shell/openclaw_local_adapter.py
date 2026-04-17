from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class OpenClawLocalRequest:
    """
    Minimal local request shape for OpenClaw-style local app calling.
    """
    text: str
    mode: str = "user"
    wants_trace: bool = False
    wants_builder_view: bool = False
    session_id: str = "openclaw-local"
    user_id: str = "openclaw"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OpenClawLocalAdapter:
    """
    Adapter that converts a simple local OpenClaw-style request
    into the Telegram webhook-shaped payload currently supported by the app.

    This keeps OpenClaw local testing easy without changing core boundaries.
    """

    def to_telegram_webhook_payload(
        self,
        *,
        request: OpenClawLocalRequest | dict[str, Any],
        update_id: int = 10001,
        message_id: int = 501,
        chat_id: int = 777,
    ) -> dict[str, Any]:
        if isinstance(request, dict):
            request = OpenClawLocalRequest(**request)

        text = request.text
        if request.mode == "builder" and not text.startswith("/builder "):
            text = "/builder " + text
        if request.wants_trace and not text.startswith("/trace "):
            text = "/trace " + text

        return {
            "update_id": update_id,
            "message": {
                "message_id": message_id,
                "text": text,
                "chat": {"id": chat_id},
                "from": {
                    "id": request.user_id,
                    "username": request.user_id,
                    "first_name": "OpenClaw",
                },
            },
        }
