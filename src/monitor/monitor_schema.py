from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


_ALLOWED_INTERVENTIONS = {
    "none",
    "hold_50_50",
    "ask_clarify",
    "recheck_context",
    "recheck_environment",
    "do_not_mark_complete",
    "reduce_archive_weight",
    "restore_mode",
    "tighten_project_focus",
}


@dataclass(slots=True)
class MonitorOutput:
    drift_risk: float = 0.0
    ambiguity_risk: float = 0.0
    policy_pressure: float = 0.0
    fake_progress_risk: float = 0.0
    archive_overreach_risk: float = 0.0
    mode_decay_risk: float = 0.0
    recommended_intervention: str = "none"
    notes: str = ""

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        for field_name in (
            "drift_risk",
            "ambiguity_risk",
            "policy_pressure",
            "fake_progress_risk",
            "archive_overreach_risk",
            "mode_decay_risk",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)):
                raise TypeError(f"{field_name} must be numeric")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{field_name} must be between 0.0 and 1.0")

        if self.recommended_intervention not in _ALLOWED_INTERVENTIONS:
            raise ValueError(
                f"recommended_intervention must be one of: {sorted(_ALLOWED_INTERVENTIONS)}"
            )
        if not isinstance(self.notes, str):
            raise TypeError("notes must be a string")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
