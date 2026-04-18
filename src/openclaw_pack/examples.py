from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openclaw_pack.adapter import OpenClawLocalAdapter
from openclaw_pack.contracts import OpenClawLocalRequest


@dataclass(slots=True)
class OpenClawLocalClientExamples:
    """
    Helper for building example local payloads for OpenClaw/manual testing.
    """

    adapter: OpenClawLocalAdapter

    def example_user_payload(self) -> dict[str, Any]:
        return self.adapter.to_runtime_request(
            request=OpenClawLocalRequest(
                text="hello there",
                mode="user",
            )
        )

    def example_builder_payload(self) -> dict[str, Any]:
        return self.adapter.to_runtime_request(
            request=OpenClawLocalRequest(
                text="inspect current run",
                mode="builder",
            )
        )

    def example_runtime_payload(self) -> dict[str, Any]:
        return self.adapter.to_runtime_request(
            request=OpenClawLocalRequest(
                text="Load MBB daily data",
                mode="builder",
            )
        )
