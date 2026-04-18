from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class ContextViewInput:
    active_project: str = ""
    active_mode: str = ""
    current_task: str = ""
    current_environment_state: str = ""
    last_verified_result: str = ""
    open_obligations: list[str] | None = None
    verification_status: str = ""
    disagreement_events: list[dict[str, Any]] | None = None
    risk_hint: str = ""
    monitor_summary: dict[str, Any] | None = None
    recent_anchor_cue: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "active_project",
            "active_mode",
            "current_task",
            "current_environment_state",
            "last_verified_result",
            "verification_status",
            "risk_hint",
            "recent_anchor_cue",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a string")
        if self.open_obligations is None:
            self.open_obligations = []
        if self.disagreement_events is None:
            self.disagreement_events = []
        if not isinstance(self.open_obligations, list) or not all(isinstance(item, str) for item in self.open_obligations):
            raise TypeError("open_obligations must be list[str]")
        if not isinstance(self.disagreement_events, list) or not all(isinstance(item, dict) for item in self.disagreement_events):
            raise TypeError("disagreement_events must be list[dict]")
        if self.monitor_summary is not None and not isinstance(self.monitor_summary, dict):
            raise TypeError("monitor_summary must be dict[str, Any] | None")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ContextView:
    active_project: str
    active_mode: str
    task_focus: str
    current_environment_state: str
    last_verified_result: str
    open_obligations: list[str] | None = None
    current_risk: str = "none"
    verification_status: str = ""
    shared_disagreement_status: str = "none"
    notes: list[str] | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "active_project",
            "active_mode",
            "task_focus",
            "current_environment_state",
            "last_verified_result",
            "current_risk",
            "verification_status",
            "shared_disagreement_status",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a string")
        if self.open_obligations is None:
            self.open_obligations = []
        if self.notes is None:
            self.notes = []
        if not isinstance(self.open_obligations, list) or not all(isinstance(item, str) for item in self.open_obligations):
            raise TypeError("open_obligations must be list[str]")
        if not isinstance(self.notes, list) or not all(isinstance(item, str) for item in self.notes):
            raise TypeError("notes must be list[str]")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
