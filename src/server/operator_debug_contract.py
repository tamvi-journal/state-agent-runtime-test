from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class OperatorPayload:
    operator_snapshot: dict[str, Any]
    dashboard_snapshot: dict[str, Any]
    rendered_console: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DebugPayload:
    runtime_shape: dict[str, Any]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
