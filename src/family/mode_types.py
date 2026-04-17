from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


_ALLOWED_MODES = {"build", "paper", "playful", "50_50", "audit", "care", "execute", ""}


@dataclass(slots=True)
class ModeInferenceInput:
    current_message: str
    active_project: str = ""
    current_task: str = ""
    recent_anchor_cue: str = ""
    context_view_summary: str = ""
    action_required: bool = False
    disagreement_open: bool = False
    verification_status: str = ""
    explicit_mode_hint: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "current_message",
            "active_project",
            "current_task",
            "recent_anchor_cue",
            "context_view_summary",
            "verification_status",
            "explicit_mode_hint",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a string")
        if not self.current_message.strip():
            raise ValueError("current_message must be a non-empty string")
        if not isinstance(self.action_required, bool):
            raise TypeError("action_required must be a bool")
        if not isinstance(self.disagreement_open, bool):
            raise TypeError("disagreement_open must be a bool")
        if self.explicit_mode_hint and self.explicit_mode_hint not in _ALLOWED_MODES:
            raise ValueError(f"explicit_mode_hint must be one of: {sorted(_ALLOWED_MODES)}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ModeInferenceResult:
    active_mode: str
    confidence: float
    secondary_mode: str = ""
    reasons: list[str] | None = None

    def __post_init__(self) -> None:
        if self.active_mode not in _ALLOWED_MODES - {""}:
            raise ValueError("active_mode must be a supported canary mode")
        if self.secondary_mode and self.secondary_mode not in _ALLOWED_MODES - {""}:
            raise ValueError("secondary_mode must be a supported canary mode")
        if not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.reasons is None:
            self.reasons = []
        if not isinstance(self.reasons, list) or not all(isinstance(item, str) for item in self.reasons):
            raise TypeError("reasons must be list[str]")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
