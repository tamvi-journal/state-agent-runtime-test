from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class CompressionInput:
    context_view: dict[str, Any] | None = None
    live_state: dict[str, Any] | None = None
    delta_log_event: dict[str, Any] | None = None
    recent_anchor_cue: str = ""
    verification_status: str = ""
    disagreement_open: bool = False
    current_question: str = ""
    task_focus: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "recent_anchor_cue",
            "verification_status",
            "current_question",
            "task_focus",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a string")
        if self.context_view is None:
            self.context_view = {}
        if self.live_state is None:
            self.live_state = {}
        if self.delta_log_event is None:
            self.delta_log_event = {}
        if not isinstance(self.context_view, dict):
            raise TypeError("context_view must be dict[str, Any] | None")
        if not isinstance(self.live_state, dict):
            raise TypeError("live_state must be dict[str, Any] | None")
        if not isinstance(self.delta_log_event, dict):
            raise TypeError("delta_log_event must be dict[str, Any] | None")
        if not isinstance(self.disagreement_open, bool):
            raise TypeError("disagreement_open must be a bool")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CompressionSummary:
    active_question: str
    main_points: list[str] | None = None
    caution: str = ""
    anchor_cue: str = ""
    next_state_hint: str = ""

    def __post_init__(self) -> None:
        for field_name in ("active_question", "caution", "anchor_cue", "next_state_hint"):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a string")
        if self.main_points is None:
            self.main_points = []
        if not isinstance(self.main_points, list) or not all(isinstance(item, str) for item in self.main_points):
            raise TypeError("main_points must be list[str]")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
