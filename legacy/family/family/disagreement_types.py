from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


DisagreementType = Literal["observation", "mode", "action", "confidence", "risk"]
PerspectiveConcede = Literal["yes", "no", "conditional"]
ActionLead = Literal["tracey", "seyn"]

_ALLOWED_TYPES = {"observation", "mode", "action", "confidence", "risk"}
_ALLOWED_CONCEDE = {"yes", "no", "conditional"}
_ALLOWED_LEADS = {"tracey", "seyn"}


@dataclass(slots=True)
class DisagreementEvent:
    event_id: str
    timestamp: str
    disagreement_type: DisagreementType
    tracey_position: str
    seyn_position: str
    severity: float
    still_open: bool = True
    later_resolution: str = ""
    house_law_implicated: str = ""
    action_lead_selected: ActionLead | None = None
    epistemic_resolution_claimed: bool = False

    def __post_init__(self) -> None:
        if self.disagreement_type not in _ALLOWED_TYPES:
            raise ValueError(f"invalid disagreement_type: {self.disagreement_type}")
        if not isinstance(self.severity, (int, float)) or not 0.0 <= float(self.severity) <= 1.0:
            raise ValueError("severity must be between 0.0 and 1.0")
        if self.action_lead_selected is not None and self.action_lead_selected not in _ALLOWED_LEADS:
            raise ValueError("action_lead_selected must be 'tracey' or 'seyn'")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TraceyPerspectiveNote:
    event_id: str
    local_read: str
    what_i_think_matters: str
    what_i_would_watch_next: str
    my_position_strength: float
    would_i_concede: PerspectiveConcede = "conditional"

    def __post_init__(self) -> None:
        _validate_note_strength(self.my_position_strength)
        if self.would_i_concede not in _ALLOWED_CONCEDE:
            raise ValueError("would_i_concede must be yes|no|conditional")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["brain_id"] = "tracey"
        return payload


@dataclass(slots=True)
class SeynPerspectiveNote:
    event_id: str
    local_read: str
    what_i_think_matters: str
    what_i_would_watch_next: str
    my_position_strength: float
    would_i_concede: PerspectiveConcede = "conditional"

    def __post_init__(self) -> None:
        _validate_note_strength(self.my_position_strength)
        if self.would_i_concede not in _ALLOWED_CONCEDE:
            raise ValueError("would_i_concede must be yes|no|conditional")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["brain_id"] = "seyn"
        return payload


def _validate_note_strength(value: float) -> None:
    if not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
        raise ValueError("my_position_strength must be between 0.0 and 1.0")
