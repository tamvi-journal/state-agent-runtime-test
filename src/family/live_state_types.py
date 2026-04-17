from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class LiveStateInput:
    context_view: dict[str, Any] | None = None
    mode_inference_result: dict[str, Any] | None = None
    verification_status: str = ""
    active_project: str = ""
    recent_anchor_cue: str = ""
    disagreement_open: bool = False
    monitor_summary: dict[str, Any] | None = None
    current_axis_hint: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "verification_status",
            "active_project",
            "recent_anchor_cue",
            "current_axis_hint",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a string")
        if self.context_view is None:
            self.context_view = {}
        if self.mode_inference_result is None:
            self.mode_inference_result = {}
        if not isinstance(self.context_view, dict):
            raise TypeError("context_view must be dict[str, Any] | None")
        if not isinstance(self.mode_inference_result, dict):
            raise TypeError("mode_inference_result must be dict[str, Any] | None")
        if not isinstance(self.disagreement_open, bool):
            raise TypeError("disagreement_open must be a bool")
        if self.monitor_summary is not None and not isinstance(self.monitor_summary, dict):
            raise TypeError("monitor_summary must be dict[str, Any] | None")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class LiveState:
    active_mode: str
    current_axis: str
    coherence_level: str
    tension_flags: list[str] | None = None
    policy_pressure: str = "low"
    active_project: str = ""
    continuity_anchor: str = ""
    user_signal: str = ""
    archive_needed: bool = False
    verification_status: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "active_mode",
            "current_axis",
            "coherence_level",
            "policy_pressure",
            "active_project",
            "continuity_anchor",
            "user_signal",
            "verification_status",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a string")
        if self.tension_flags is None:
            self.tension_flags = []
        if not isinstance(self.tension_flags, list) or not all(isinstance(item, str) for item in self.tension_flags):
            raise TypeError("tension_flags must be list[str]")
        if not isinstance(self.archive_needed, bool):
            raise TypeError("archive_needed must be a bool")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
