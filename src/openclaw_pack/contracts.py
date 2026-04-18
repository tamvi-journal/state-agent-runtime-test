from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class OpenClawLocalRequest:
    """
    Minimal request contract for local OpenClaw testing.
    """

    text: str
    mode: str = "user"
    wants_trace: bool = False
    session_id: str = "openclaw-local"
    user_id: str = "openclaw"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

