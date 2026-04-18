from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class ReactivationInput:
    current_message: str
    detected_cues: list[str] | None = None
    active_project_hint: str = ""
    compression_summary: dict[str, Any] | None = None
    context_view: dict[str, Any] | None = None
    live_state: dict[str, Any] | None = None
    recent_anchor_cue: str = ""
    disagreement_open: bool = False
    verification_status: str = ""
    mode_hint: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "current_message",
            "active_project_hint",
            "recent_anchor_cue",
            "verification_status",
            "mode_hint",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a string")
        if not self.current_message.strip():
            raise ValueError("current_message must be a non-empty string")
        if self.detected_cues is None:
            self.detected_cues = []
        if self.compression_summary is None:
            self.compression_summary = {}
        if self.context_view is None:
            self.context_view = {}
        if self.live_state is None:
            self.live_state = {}
        if not isinstance(self.detected_cues, list) or not all(isinstance(item, str) for item in self.detected_cues):
            raise TypeError("detected_cues must be list[str]")
        if not isinstance(self.compression_summary, dict):
            raise TypeError("compression_summary must be dict[str, Any] | None")
        if not isinstance(self.context_view, dict):
            raise TypeError("context_view must be dict[str, Any] | None")
        if not isinstance(self.live_state, dict):
            raise TypeError("live_state must be dict[str, Any] | None")
        if not isinstance(self.disagreement_open, bool):
            raise TypeError("disagreement_open must be a bool")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReactivationResult:
    reactivation_triggered: bool
    matched_cues: list[str] | None = None
    restored_mode: str = ""
    restored_axis_hint: str = ""
    restored_project: str = ""
    confidence: float = 0.0
    notes: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.reactivation_triggered, bool):
            raise TypeError("reactivation_triggered must be a bool")
        if self.matched_cues is None:
            self.matched_cues = []
        if not isinstance(self.matched_cues, list) or not all(isinstance(item, str) for item in self.matched_cues):
            raise TypeError("matched_cues must be list[str]")
        for field_name in ("restored_mode", "restored_axis_hint", "restored_project", "notes"):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a string")
        if not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
