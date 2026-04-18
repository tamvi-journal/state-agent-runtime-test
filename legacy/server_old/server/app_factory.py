from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from server.fastapi_adapter import FastAPIAdapter
from server.live_webhook_server import LiveWebhookServer
from server.runtime_provider import RuntimeProvider


@dataclass(slots=True)
class AppFactory:
    """
    Framework-facing app skeleton with a realer runtime provider.
    """

    runtime_provider: RuntimeProvider = field(default_factory=RuntimeProvider)
    adapter: FastAPIAdapter = field(default_factory=lambda: FastAPIAdapter(live_webhook_server=LiveWebhookServer()))

    def handle_health(self) -> dict[str, Any]:
        return self.adapter.health()

    def handle_ready(self) -> dict[str, Any]:
        return self.adapter.ready()

    def handle_telegram_webhook(
        self,
        *,
        method: str,
        headers: dict[str, Any],
        json_body: dict[str, Any],
    ) -> dict[str, Any]:
        text = str(
            json_body.get("message", {}).get("text", "hello there")
        )
        runtime_result = self.runtime_provider.get_runtime_result(user_text=text)
        return self.adapter.handle_webhook(
            method=method,
            path="/webhooks/telegram",
            headers=headers,
            json_body=json_body,
            runtime_result=runtime_result,
        )
