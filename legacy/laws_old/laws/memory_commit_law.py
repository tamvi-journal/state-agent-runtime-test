from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


_ALLOWED_CLASSES = {"persist", "archive", "candidate_only", "ephemeral"}


@dataclass(slots=True)
class MemoryCommitDecision:
    commit_allowed: bool
    persistence_class: str
    reason: str

    def __post_init__(self) -> None:
        if self.persistence_class not in _ALLOWED_CLASSES:
            raise ValueError(f"invalid persistence_class: {self.persistence_class}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MemoryCommitLaw:
    """
    Runtime memory commit should go through explicit rules.
    """

    def evaluate(
        self,
        *,
        object_type: str,
        load_bearing: bool = False,
        verified: bool = False,
        unresolved: bool = False,
    ) -> MemoryCommitDecision:
        if object_type == "disagreement_event" and unresolved:
            return MemoryCommitDecision(
                commit_allowed=True,
                persistence_class="persist",
                reason="unresolved disagreement is load-bearing for plurality continuity",
            )

        if object_type in {"tracey_memory_item", "seyn_ledger_entry"} and load_bearing:
            return MemoryCommitDecision(
                commit_allowed=True,
                persistence_class="persist",
                reason="load-bearing child memory may commit",
            )

        if object_type == "worker_payload" and verified:
            return MemoryCommitDecision(
                commit_allowed=True,
                persistence_class="archive",
                reason="verified worker output may archive",
            )

        return MemoryCommitDecision(
            commit_allowed=False,
            persistence_class="candidate_only",
            reason="memory commit is not allowed without explicit structural conditions",
        )
