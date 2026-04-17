from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from state.archive_router import ArchiveRouter


@dataclass(slots=True)
class PluralityPersistenceSnapshotBuilder:
    """
    Build a compact persistence snapshot for plurality-related objects.
    """

    archive_router: ArchiveRouter

    def build(
        self,
        *,
        disagreement_event: dict[str, Any] | None = None,
        local_notes: list[dict[str, Any]] | None = None,
        reconciliation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        disagreement_event = disagreement_event or {}
        local_notes = local_notes or []
        reconciliation = reconciliation or {}

        unresolved = bool(disagreement_event.get("still_open", False))

        event_route = self.archive_router.route(
            object_type="disagreement_event",
            payload=disagreement_event,
            unresolved=unresolved,
            verified=not unresolved,
        ) if disagreement_event else None

        note_routes = [
            self.archive_router.route(
                object_type="local_perspective_note",
                payload=note,
                unresolved=unresolved,
            )
            for note in local_notes
        ]

        reconciliation_route = self.archive_router.route(
            object_type="reconciliation_result",
            payload=reconciliation,
            unresolved=(reconciliation.get("reconciliation_state") in {"remain_open", "partial_convergence", "temporary_operational_alignment"}),
        ) if reconciliation else None

        return {
            "disagreement_event": event_route,
            "local_perspective_notes": note_routes,
            "reconciliation_result": reconciliation_route,
        }
