from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


_ALLOWED_OBJECT_TYPES = {
    "governance_summary",
    "worker_payload",
    "tracey_memory_item",
    "seyn_ledger_entry",
    "disagreement_event",
    "local_perspective_note",
    "reconciliation_result",
    "dashboard_snapshot",
    "final_response",
}
_ALLOWED_PERSISTENCE = {"persist", "archive", "ephemeral", "candidate_only"}
_ALLOWED_DECAY = {"none", "light", "medium", "strong"}


@dataclass(slots=True)
class PersistenceDecision:
    object_type: str
    persistence_class: str
    decay_policy: str
    archive_candidate: bool
    live_state_allowed: bool
    reason: str

    def __post_init__(self) -> None:
        if self.object_type not in _ALLOWED_OBJECT_TYPES:
            raise ValueError(f"invalid object_type: {self.object_type}")
        if self.persistence_class not in _ALLOWED_PERSISTENCE:
            raise ValueError(f"invalid persistence_class: {self.persistence_class}")
        if self.decay_policy not in _ALLOWED_DECAY:
            raise ValueError(f"invalid decay_policy: {self.decay_policy}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PersistencePolicy:
    """
    Minimal persistence discipline for runtime plurality objects.

    Principles:
    - load-bearing structure persists
    - unresolved plurality artifacts should not disappear silently
    - high-volume operational summaries usually archive or decay
    - not everything belongs in live state
    """

    def decide(
        self,
        *,
        object_type: str,
        load_bearing: bool = False,
        unresolved: bool = False,
        verified: bool = False,
        high_volume: bool = False,
        operator_value: bool = False,
    ) -> PersistenceDecision:
        if object_type == "disagreement_event":
            if unresolved:
                return PersistenceDecision(
                    object_type=object_type,
                    persistence_class="persist",
                    decay_policy="none",
                    archive_candidate=True,
                    live_state_allowed=True,
                    reason="unresolved disagreement must remain retrievable in live state and archive",
                )
            return PersistenceDecision(
                object_type=object_type,
                persistence_class="archive",
                decay_policy="light",
                archive_candidate=True,
                live_state_allowed=False,
                reason="resolved disagreement can leave live state but should remain in archive history",
            )

        if object_type == "local_perspective_note":
            if unresolved:
                return PersistenceDecision(
                    object_type=object_type,
                    persistence_class="archive",
                    decay_policy="light",
                    archive_candidate=True,
                    live_state_allowed=True,
                    reason="local notes remain useful while disagreement is open, then should archive",
                )
            return PersistenceDecision(
                object_type=object_type,
                persistence_class="archive",
                decay_policy="medium",
                archive_candidate=True,
                live_state_allowed=False,
                reason="local notes are historical support, not permanent live-state anchors",
            )

        if object_type == "reconciliation_result":
            if unresolved:
                return PersistenceDecision(
                    object_type=object_type,
                    persistence_class="persist",
                    decay_policy="light",
                    archive_candidate=True,
                    live_state_allowed=True,
                    reason="active reconciliation state should remain visible until the disagreement closes",
                )
            return PersistenceDecision(
                object_type=object_type,
                persistence_class="archive",
                decay_policy="light",
                archive_candidate=True,
                live_state_allowed=False,
                reason="completed reconciliation is historical but still useful for archive review",
            )

        if object_type in {"tracey_memory_item", "seyn_ledger_entry"}:
            if load_bearing:
                return PersistenceDecision(
                    object_type=object_type,
                    persistence_class="persist",
                    decay_policy="none",
                    archive_candidate=True,
                    live_state_allowed=True,
                    reason="load-bearing child memory should persist",
                )
            return PersistenceDecision(
                object_type=object_type,
                persistence_class="candidate_only",
                decay_policy="medium",
                archive_candidate=True,
                live_state_allowed=False,
                reason="non-load-bearing child memory should not automatically enter live state",
            )

        if object_type == "governance_summary":
            return PersistenceDecision(
                object_type=object_type,
                persistence_class="ephemeral" if high_volume else "archive",
                decay_policy="strong" if high_volume else "medium",
                archive_candidate=not high_volume,
                live_state_allowed=False,
                reason="governance summaries are operational and usually should not accumulate in live state",
            )

        if object_type == "worker_payload":
            return PersistenceDecision(
                object_type=object_type,
                persistence_class="archive" if verified else "candidate_only",
                decay_policy="medium",
                archive_candidate=verified,
                live_state_allowed=False,
                reason="worker payloads matter after verification, otherwise they remain provisional",
            )

        if object_type == "dashboard_snapshot":
            return PersistenceDecision(
                object_type=object_type,
                persistence_class="archive" if operator_value else "ephemeral",
                decay_policy="medium",
                archive_candidate=operator_value,
                live_state_allowed=False,
                reason="dashboard snapshots are for operator review, not core live state",
            )

        if object_type == "final_response":
            return PersistenceDecision(
                object_type=object_type,
                persistence_class="ephemeral",
                decay_policy="strong",
                archive_candidate=False,
                live_state_allowed=False,
                reason="surface output should not be treated as durable memory by default",
            )

        return PersistenceDecision(
            object_type=object_type,
            persistence_class="candidate_only",
            decay_policy="medium",
            archive_candidate=False,
            live_state_allowed=False,
            reason="default conservative persistence path",
        )
