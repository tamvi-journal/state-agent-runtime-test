from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any


_ALLOWED_TYPES = {"observation", "mode", "action", "confidence", "risk"}
_ALLOWED_CONCEDE = {"yes", "no", "conditional"}


@dataclass(slots=True)
class DisagreementEvent:
    event_id: str
    timestamp: str
    disagreement_type: str
    tracey_position: str
    seyn_position: str
    severity: float
    still_open: bool = True
    later_resolution: str = ""
    house_law_implicated: str | None = None
    action_lead_selected: str | None = None
    epistemic_resolution_claimed: bool = False

    def __post_init__(self) -> None:
        if self.disagreement_type not in _ALLOWED_TYPES:
            raise ValueError(f"invalid disagreement_type: {self.disagreement_type}")
        if not isinstance(self.severity, (int, float)) or not 0.0 <= float(self.severity) <= 1.0:
            raise ValueError("severity must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class LocalPerspectiveNote:
    brain_id: str
    event_id: str
    local_read: str
    what_i_think_matters: str
    what_i_would_watch_next: str
    my_position_strength: float
    would_i_concede: str = "conditional"

    def __post_init__(self) -> None:
        if self.brain_id not in {"tracey", "seyn"}:
            raise ValueError("brain_id must be 'tracey' or 'seyn'")
        if self.would_i_concede not in _ALLOWED_CONCEDE:
            raise ValueError("would_i_concede must be yes|no|conditional")
        if not isinstance(self.my_position_strength, (int, float)) or not 0.0 <= float(self.my_position_strength) <= 1.0:
            raise ValueError("my_position_strength must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
