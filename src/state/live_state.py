from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


ALLOWED_ACTIVE_MODES = {"paper", "build", "playful", "50_50", "audit"}
ALLOWED_AXES = {"mechanism_first", "relational", "technical", "exploratory"}


@dataclass(slots=True)
class LiveState:
    """
    Small operational state for the main brain.

    Notes:
    - This is not long-term memory.
    - This is not transcript replay.
    - This is only the current operating posture of the system.
    """

    active_mode: str
    current_axis: str
    coherence_level: float
    tension_flags: list[str] = field(default_factory=list)
    active_project: str = ""
    user_signal: str = ""
    continuity_anchor: str = ""
    archive_needed: bool = False

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Raise ValueError / TypeError if the state shape is invalid."""
        if self.active_mode not in ALLOWED_ACTIVE_MODES:
            raise ValueError(
                f"Invalid active_mode={self.active_mode!r}. "
                f"Allowed: {sorted(ALLOWED_ACTIVE_MODES)}"
            )

        if self.current_axis not in ALLOWED_AXES:
            raise ValueError(
                f"Invalid current_axis={self.current_axis!r}. "
                f"Allowed: {sorted(ALLOWED_AXES)}"
            )

        if not isinstance(self.coherence_level, (int, float)):
            raise TypeError("coherence_level must be a number")
        if not 0.0 <= float(self.coherence_level) <= 1.0:
            raise ValueError("coherence_level must be between 0.0 and 1.0")

        if not isinstance(self.tension_flags, list):
            raise TypeError("tension_flags must be a list[str]")
        if not all(isinstance(item, str) for item in self.tension_flags):
            raise TypeError("tension_flags must contain only strings")

        if not isinstance(self.active_project, str):
            raise TypeError("active_project must be a string")
        if not isinstance(self.user_signal, str):
            raise TypeError("user_signal must be a string")
        if not isinstance(self.continuity_anchor, str):
            raise TypeError("continuity_anchor must be a string")
        if not isinstance(self.archive_needed, bool):
            raise TypeError("archive_needed must be a bool")

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dict."""
        return {
            "active_mode": self.active_mode,
            "current_axis": self.current_axis,
            "coherence_level": float(self.coherence_level),
            "tension_flags": list(self.tension_flags),
            "active_project": self.active_project,
            "user_signal": self.user_signal,
            "continuity_anchor": self.continuity_anchor,
            "archive_needed": self.archive_needed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LiveState":
        """Build a LiveState from a dict."""
        return cls(
            active_mode=data["active_mode"],
            current_axis=data["current_axis"],
            coherence_level=float(data["coherence_level"]),
            tension_flags=list(data.get("tension_flags", [])),
            active_project=str(data.get("active_project", "")),
            user_signal=str(data.get("user_signal", "")),
            continuity_anchor=str(data.get("continuity_anchor", "")),
            archive_needed=bool(data.get("archive_needed", False)),
        )

    def updated(self, **changes: Any) -> "LiveState":
        """
        Return a new validated LiveState with selected fields changed.
        This keeps updates explicit and validation always-on.
        """
        data = self.to_dict()
        data.update(changes)
        return LiveState.from_dict(data)
