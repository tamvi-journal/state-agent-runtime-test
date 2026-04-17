from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from server.webhook_route_table import WebhookRouteTable
from server.webhook_server_contract import WebhookHttpRequest, WebhookHttpResponse
from server.webhook_server_policy import WebhookServerPolicy
from transport.telegram_webhook_bridge import TelegramWebhookBridge
from transport.telegram_webhook_response import build_webhook_response


@dataclass(slots=True)
class LiveWebhookServer:
    """
    Live webhook skeleton.

    This is still framework-free.
    It accepts an HTTP-like request object and returns an HTTP-like response object.

    Purpose:
    - keep HTTP boundary separate from transport boundary
    - keep transport boundary separate from shell/runtime boundary
    """

    route_table: WebhookRouteTable = field(default_factory=WebhookRouteTable)
    policy: WebhookServerPolicy = field(default_factory=WebhookServerPolicy)
    telegram_bridge: TelegramWebhookBridge = field(default_factory=TelegramWebhookBridge)

    def handle(
        self,
        *,
        request: WebhookHttpRequest | dict[str, Any],
        runtime_result: dict[str, Any],
    ) -> WebhookHttpResponse:
        if isinstance(request, dict):
            request = WebhookHttpRequest(**request)

        transport = self.route_table.resolve(request.path)
        policy = self.policy.decide(
            transport=transport,
            method=request.method,
            json_body=request.json_body,
        )

        if not policy.accepted:
            return WebhookHttpResponse(
                status="rejected",
                http_code=policy.http_code,
                body={
                    "ok": False,
                    "reason": policy.reason,
                    "transport": transport,
                },
            )

        if transport == "telegram":
            bridge_result = self.telegram_bridge.handle_webhook(
                webhook_payload=request.json_body,
                runtime_result=runtime_result,
            )
            webhook_response = build_webhook_response(
                transport_result=bridge_result["transport_result"],
            )
            return WebhookHttpResponse(
                status="accepted" if webhook_response.accepted else "rejected",
                http_code=200 if webhook_response.accepted else 502,
                body=webhook_response.to_dict(),
            )

        return WebhookHttpResponse(
            status="rejected",
            http_code=501,
            body={
                "ok": False,
                "reason": "transport route exists but no live handler is implemented",
                "transport": transport,
            },
        )
