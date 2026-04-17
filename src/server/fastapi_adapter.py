from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from server.live_webhook_server import LiveWebhookServer
from server.webhook_server_contract import WebhookHttpRequest


@dataclass(slots=True)
class FastAPIAdapter:
    """
    Framework adapter layer.

    This does not require FastAPI itself.
    It converts framework-shaped request data into internal server contracts.
    """

    live_webhook_server: LiveWebhookServer

    def handle_webhook(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, Any],
        json_body: dict[str, Any],
        runtime_result: dict[str, Any],
    ) -> dict[str, Any]:
        request = WebhookHttpRequest(
            method=method,
            path=path,
            headers=headers,
            json_body=json_body,
        )
        response = self.live_webhook_server.handle(
            request=request,
            runtime_result=runtime_result,
        )
        return response.to_dict()

    @staticmethod
    def health() -> dict[str, Any]:
        return {
            "ok": True,
            "status": "healthy",
        }

    @staticmethod
    def ready() -> dict[str, Any]:
        return {
            "ok": True,
            "status": "ready",
        }
