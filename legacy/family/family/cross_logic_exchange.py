from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


_ALLOWED_BRAIN_IDS = {"tracey", "seyn"}


@dataclass(slots=True)
class CrossLogicExchange:
    """
    One child's explicit articulation of its logic in a disagreement.

    This is not just a position.
    It is the structure behind the position.
    """

    brain_id: str
    event_id: str
    claim: str
    mechanism: str
    evidence_or_signal: str
    what_would_change_my_mind: str
    concession_boundary: str

    def __post_init__(self) -> None:
        if self.brain_id not in _ALLOWED_BRAIN_IDS:
            raise ValueError("brain_id must be 'tracey' or 'seyn'")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
