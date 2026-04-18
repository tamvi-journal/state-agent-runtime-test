from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from state.persistence_policy import PersistencePolicy


@dataclass(slots=True)
class ArchiveRouter:
    """
    Small helper that applies persistence policy and returns routing hints.
    """

    policy: PersistencePolicy = field(default_factory=PersistencePolicy)

    def route(
        self,
        *,
        object_type: str,
        payload: dict[str, Any],
        load_bearing: bool = False,
        unresolved: bool = False,
        verified: bool = False,
        high_volume: bool = False,
        operator_value: bool = False,
    ) -> dict[str, Any]:
        decision = self.policy.decide(
            object_type=object_type,
            load_bearing=load_bearing,
            unresolved=unresolved,
            verified=verified,
            high_volume=high_volume,
            operator_value=operator_value,
        )

        return {
            "decision": decision.to_dict(),
            "should_write_live_state": decision.live_state_allowed,
            "should_write_archive": decision.archive_candidate,
            "should_decay_quickly": decision.decay_policy in {"medium", "strong"},
            "payload": payload,
        }
