from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


EvidenceAuthority = Literal["authoritative", "operator_reported", "weak"]

_ALLOWED_AUTHORITIES = {"authoritative", "operator_reported", "weak"}


@dataclass(slots=True)
class ObservedOutcome:
    observed_outcome: str = ""
    evidence_source: str = ""
    evidence_authority: EvidenceAuthority = "weak"
    observed_at: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        for field_name in ("observed_outcome", "evidence_source", "observed_at", "notes"):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a string")
        if self.evidence_authority not in _ALLOWED_AUTHORITIES:
            raise ValueError(f"evidence_authority must be one of: {sorted(_ALLOWED_AUTHORITIES)}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
