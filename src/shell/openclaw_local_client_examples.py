from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shell.openclaw_local_adapter import OpenClawLocalAdapter, OpenClawLocalRequest


@dataclass(slots=True)
class OpenClawLocalClientExamples:
    """
    Helper for building example local payloads for OpenClaw/manual testing.
    """

    adapter: OpenClawLocalAdapter

    def example_user_payload(self) -> dict[str, Any]:
        return self.adapter.to_telegram_webhook_payload(
            request=OpenClawLocalRequest(
                text="hello there",
                mode="user",
            )
        )

    def example_builder_payload(self) -> dict[str, Any]:
        return self.adapter.to_telegram_webhook_payload(
            request=OpenClawLocalRequest(
                text="inspect current run",
                mode="builder",
                wants_builder_view=True,
            )
        )

    def example_runtime_payload(self) -> dict[str, Any]:
        return self.adapter.to_telegram_webhook_payload(
            request=OpenClawLocalRequest(
                text="Tracey, this is home, but verify whether MBB daily data is actually done.",
                mode="builder",
                wants_builder_view=True,
            )
        )
