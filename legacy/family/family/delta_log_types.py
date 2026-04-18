from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class DeltaLogInput:
    previous_live_state: dict[str, Any]
    current_live_state: dict[str, Any]
    recent_trigger_cue: str = ""
    archive_consulted: bool = False
    verification_before: str = ""
    verification_after: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.previous_live_state, dict):
            raise TypeError("previous_live_state must be dict[str, Any]")
        if not isinstance(self.current_live_state, dict):
            raise TypeError("current_live_state must be dict[str, Any]")
        if not isinstance(self.recent_trigger_cue, str):
            raise TypeError("recent_trigger_cue must be a string")
        if not isinstance(self.archive_consulted, bool):
            raise TypeError("archive_consulted must be a bool")
        if not isinstance(self.verification_before, str):
            raise TypeError("verification_before must be a string")
        if not isinstance(self.verification_after, str):
            raise TypeError("verification_after must be a string")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DeltaLogEvent:
    mode_shift: str = "none"
    coherence_shift: str = "flat"
    policy_intrusion_detected: bool = False
    repair_event: bool = False
    ambiguity_unresolved: bool = False
    trigger_cue: str = ""
    archive_consulted: bool = False
    verification_changed: str = "none"
    notes: list[str] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.mode_shift, str):
            raise TypeError("mode_shift must be a string")
        if self.coherence_shift not in {"up", "down", "flat"}:
            raise ValueError("coherence_shift must be up|down|flat")
        for field_name in (
            "policy_intrusion_detected",
            "repair_event",
            "ambiguity_unresolved",
            "archive_consulted",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise TypeError(f"{field_name} must be a bool")
        if not isinstance(self.trigger_cue, str):
            raise TypeError("trigger_cue must be a string")
        if not isinstance(self.verification_changed, str):
            raise TypeError("verification_changed must be a string")
        if self.notes is None:
            self.notes = []
        if not isinstance(self.notes, list) or not all(isinstance(item, str) for item in self.notes):
            raise TypeError("notes must be list[str]")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
