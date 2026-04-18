from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class TelegramWebhookResponse:
    """
    Normalized response object for a future webhook handler.

    It says whether the webhook call itself was accepted by the local system,
    not whether Telegram network delivery has already happened.
    """

    accepted: bool
    status: str
    reason: str
    outbound_message: dict[str, Any] | None = None
    ack: dict[str, Any] | None = None
    error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_webhook_response(*, transport_result: dict[str, Any]) -> TelegramWebhookResponse:
    if transport_result.get("error") is not None:
        return TelegramWebhookResponse(
            accepted=False,
            status="rejected",
            reason=str(transport_result["error"].get("reason", "transport failure")),
            outbound_message=None,
            ack=transport_result.get("ack"),
            error=transport_result.get("error"),
        )

    return TelegramWebhookResponse(
        accepted=True,
        status="accepted",
        reason="webhook payload parsed and routed successfully",
        outbound_message=transport_result.get("transport_outbound"),
        ack=transport_result.get("ack"),
        error=None,
    )
