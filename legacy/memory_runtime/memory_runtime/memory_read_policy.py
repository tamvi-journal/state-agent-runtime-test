from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class MemoryReadDecision:
    may_read_live_state: bool
    may_read_archive: bool
    may_read_family_memory: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MemoryReadPolicy:
    """
    Controls which memory planes may be consulted at runtime.
    """

    def decide(
        self,
        *,
        task_type: str,
        active_mode: str,
        archive_needed: bool,
        family_signal_detected: bool,
    ) -> MemoryReadDecision:
        may_read_live_state = True
        may_read_archive = archive_needed or task_type in {"research", "architecture", "audit"}
        may_read_family_memory = family_signal_detected or active_mode in {"home", "care"}

        return MemoryReadDecision(
            may_read_live_state=may_read_live_state,
            may_read_archive=may_read_archive,
            may_read_family_memory=may_read_family_memory,
            reason="memory access derived from task type, mode, and explicit archive/family need",
        )
