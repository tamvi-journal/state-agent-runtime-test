from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DeltaRecord:
    """
    Tracks what shifted most recently.

    State = where the system is
    Delta = how the system just moved
    """

    mode_shift: str = ""
    coherence_shift: float = 0.0
    policy_intrusion_detected: bool = False
    repair_event: bool = False
    trigger_cue: str = ""
    archive_consulted: bool = False

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.mode_shift, str):
            raise TypeError("mode_shift must be a string")

        if not isinstance(self.coherence_shift, (int, float)):
            raise TypeError("coherence_shift must be a number")
        if not -1.0 <= float(self.coherence_shift) <= 1.0:
            raise ValueError("coherence_shift must be between -1.0 and 1.0")

        if not isinstance(self.policy_intrusion_detected, bool):
            raise TypeError("policy_intrusion_detected must be a bool")
        if not isinstance(self.repair_event, bool):
            raise TypeError("repair_event must be a bool")
        if not isinstance(self.trigger_cue, str):
            raise TypeError("trigger_cue must be a string")
        if not isinstance(self.archive_consulted, bool):
            raise TypeError("archive_consulted must be a bool")

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode_shift": self.mode_shift,
            "coherence_shift": float(self.coherence_shift),
            "policy_intrusion_detected": self.policy_intrusion_detected,
            "repair_event": self.repair_event,
            "trigger_cue": self.trigger_cue,
            "archive_consulted": self.archive_consulted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeltaRecord":
        return cls(
            mode_shift=str(data.get("mode_shift", "")),
            coherence_shift=float(data.get("coherence_shift", 0.0)),
            policy_intrusion_detected=bool(data.get("policy_intrusion_detected", False)),
            repair_event=bool(data.get("repair_event", False)),
            trigger_cue=str(data.get("trigger_cue", "")),
            archive_consulted=bool(data.get("archive_consulted", False)),
        )
