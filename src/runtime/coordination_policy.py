from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class CoordinationInput:
    current_mode: str
    task_type: str
    risk_score: float = 0.0
    disagreement_severity: float = 0.0
    disagreement_detected: bool = False
    effort_level: str = ""
    verification_requirement: str = ""
    monitor_intensity: str = ""
    disagreement_handling: str = ""
    primary_risk: str = "none"
    recommended_intervention: str = "none"
    user_preference: str | None = None
    tracey_recognition_signal: bool = False
    seyn_verification_signal: bool = False
    seyn_disagreement_signal: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CoordinationDecision:
    lead_brain_for_action: str | None
    support_brain: str | None
    hold_for_more_input: bool
    surface_disagreement_to_user: bool
    hold_reason: str
    routing_reason: str
    policy_flags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
