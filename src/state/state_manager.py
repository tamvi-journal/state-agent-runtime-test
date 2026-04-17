from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .delta_log import DeltaRecord
from .live_state import LiveState


@dataclass(slots=True)
class StateManager:
    """
    Owns the current live state plus recent delta records.

    Responsibilities:
    - keep the current state valid
    - keep recent deltas visible
    - reject malformed updates loudly
    """

    live_state: LiveState
    delta_history: list[DeltaRecord] = field(default_factory=list)
    max_delta_history: int = 20

    def __post_init__(self) -> None:
        if self.max_delta_history <= 0:
            raise ValueError("max_delta_history must be > 0")

    def get_state(self) -> LiveState:
        return self.live_state

    def get_recent_deltas(self) -> list[DeltaRecord]:
        return list(self.delta_history)

    def replace_state(self, new_state: LiveState) -> LiveState:
        if not isinstance(new_state, LiveState):
            raise TypeError("new_state must be a LiveState")
        new_state.validate()
        self.live_state = new_state
        return self.live_state

    def update_state(self, **changes: Any) -> LiveState:
        """
        Update the live state with validation.
        Returns the new validated state.
        """
        self.live_state = self.live_state.updated(**changes)
        return self.live_state

    def append_delta(self, delta: DeltaRecord) -> DeltaRecord:
        if not isinstance(delta, DeltaRecord):
            raise TypeError("delta must be a DeltaRecord")
        delta.validate()
        self.delta_history.append(delta)

        if len(self.delta_history) > self.max_delta_history:
            self.delta_history = self.delta_history[-self.max_delta_history :]

        return delta

    def append_delta_from_dict(self, data: dict[str, Any]) -> DeltaRecord:
        delta = DeltaRecord.from_dict(data)
        return self.append_delta(delta)

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable snapshot of state + recent deltas."""
        return {
            "live_state": self.live_state.to_dict(),
            "delta_history": [d.to_dict() for d in self.delta_history],
            "max_delta_history": self.max_delta_history,
        }
