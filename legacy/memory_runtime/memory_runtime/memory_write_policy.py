from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from laws.memory_commit_law import MemoryCommitLaw


@dataclass(slots=True)
class MemoryWriteDecision:
    should_write_live_state: bool
    should_write_archive: bool
    commit_allowed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MemoryWritePolicy:
    """
    Controls write-side runtime behavior using MemoryCommitLaw.
    """

    commit_law: MemoryCommitLaw

    def decide(
        self,
        *,
        object_type: str,
        load_bearing: bool = False,
        verified: bool = False,
        unresolved: bool = False,
    ) -> MemoryWriteDecision:
        decision = self.commit_law.evaluate(
            object_type=object_type,
            load_bearing=load_bearing,
            verified=verified,
            unresolved=unresolved,
        )

        return MemoryWriteDecision(
            should_write_live_state=decision.persistence_class == "persist",
            should_write_archive=decision.persistence_class in {"persist", "archive"},
            commit_allowed=decision.commit_allowed,
            reason=decision.reason,
        )
