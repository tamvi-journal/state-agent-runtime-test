from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openclaw_pack.contracts import OpenClawLocalRequest


@dataclass(slots=True)
class OpenClawLocalAdapter:
    """
    Converts a thin OpenClaw-style local request into a direct harness request.
    """

    def to_runtime_request(
        self,
        *,
        request: OpenClawLocalRequest | dict[str, Any],
    ) -> dict[str, Any]:
        if isinstance(request, dict):
            request = OpenClawLocalRequest(**request)

        return {
            "user_text": request.text,
            "render_mode": request.mode,
            "session_id": request.session_id,
            "user_id": request.user_id,
            "wants_trace": request.wants_trace,
        }
