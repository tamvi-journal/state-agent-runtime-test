from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.main_brain import MainBrain
from verification.verification_record import VerificationRecord


@dataclass(slots=True)
class RequestRouter:
    """
    Thin routing layer.

    Current phase:
    - no complex branching
    - no multi-worker routing here
    - mainly forwards normalized inputs to MainBrain
    """

    main_brain: MainBrain

    def route(
        self,
        user_text: str,
        *,
        worker_payload: dict[str, Any] | None = None,
        verification_record: VerificationRecord | None = None,
        render_mode: str = "user",
        monitor_summary: dict[str, Any] | None = None,
    ) -> str:
        return self.main_brain.handle_request(
            user_text,
            worker_payload=worker_payload,
            verification_record=verification_record,
            render_mode=render_mode,
            monitor_summary=monitor_summary,
        )