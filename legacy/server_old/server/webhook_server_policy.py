from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class WebhookServerPolicyDecision:
    accepted: bool
    reason: str
    http_code: int
    requires_json_body: bool
    trace_logging_allowed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class WebhookServerPolicy:
    """
    Small boundary policy for webhook handling.
    """

    def decide(
        self,
        *,
        transport: str | None,
        method: str,
        json_body: dict[str, Any],
    ) -> WebhookServerPolicyDecision:
        if transport is None:
            return WebhookServerPolicyDecision(
                accepted=False,
                reason="unknown webhook route",
                http_code=404,
                requires_json_body=True,
                trace_logging_allowed=False,
            )

        if method != "POST":
            return WebhookServerPolicyDecision(
                accepted=False,
                reason="webhook only accepts POST",
                http_code=405,
                requires_json_body=True,
                trace_logging_allowed=False,
            )

        if not isinstance(json_body, dict) or not json_body:
            return WebhookServerPolicyDecision(
                accepted=False,
                reason="missing json body",
                http_code=400,
                requires_json_body=True,
                trace_logging_allowed=False,
            )

        return WebhookServerPolicyDecision(
            accepted=True,
            reason="request accepted by webhook boundary",
            http_code=200,
            requires_json_body=True,
            trace_logging_allowed=False,
        )
