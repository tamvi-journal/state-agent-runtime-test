from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class HandoffBaton:
    """
    Minimal carryover object for the next turn.

    This is the only active memory artifact in the thin harness.
    It carries compact operational posture only and never replays transcript history.
    """

    task_focus: str
    active_mode: str
    open_loops: list[str]
    verification_status: str
    monitor_summary: dict[str, Any]
    next_hint: str

    def __post_init__(self) -> None:
        if not isinstance(self.task_focus, str):
            raise TypeError("task_focus must be a string")
        if not isinstance(self.active_mode, str):
            raise TypeError("active_mode must be a string")
        if not isinstance(self.open_loops, list) or not all(isinstance(item, str) for item in self.open_loops):
            raise TypeError("open_loops must be list[str]")
        if not isinstance(self.verification_status, str):
            raise TypeError("verification_status must be a string")
        if not isinstance(self.monitor_summary, dict):
            raise TypeError("monitor_summary must be dict[str, Any]")
        if not isinstance(self.next_hint, str):
            raise TypeError("next_hint must be a string")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

