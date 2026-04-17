from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OperatorConsoleSession:
    """
    Minimal in-memory operator session.

    Goal:
    let an operator inspect recent runtime snapshots
    without exposing raw internals to standard user channels.
    """

    session_id: str
    history: list[dict[str, Any]] = field(default_factory=list)

    def append(self, snapshot: dict[str, Any]) -> None:
        self.history.append(snapshot)

    def latest(self) -> dict[str, Any] | None:
        if not self.history:
            return None
        return self.history[-1]

    def summary(self) -> dict[str, Any]:
        latest = self.latest()
        return {
            "session_id": self.session_id,
            "items": len(self.history),
            "latest_available": latest is not None,
            "latest_reconciliation_state": None if latest is None else latest.get("reconciliation_state"),
            "latest_hold_for_more_input": None if latest is None else latest.get("hold_for_more_input"),
        }
