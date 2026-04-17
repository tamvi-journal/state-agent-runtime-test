from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from observability.dashboard_snapshot import DashboardSnapshotBuilder
from observability.dashboard_summary import DashboardSummaryBuilder
from observability.timeline_view import TimelineViewBuilder
from shell.operator_snapshot import OperatorSnapshotBuilder


@dataclass(slots=True)
class OperatorConsoleBridge:
    """
    Build a higher-level operator console payload from runtime artifacts.

    This sits above:
    - operator snapshot
    - dashboard snapshot
    - runtime result
    """

    operator_snapshot_builder: OperatorSnapshotBuilder = field(default_factory=OperatorSnapshotBuilder)
    dashboard_snapshot_builder: DashboardSnapshotBuilder = field(
        default_factory=lambda: DashboardSnapshotBuilder(
            summary_builder=DashboardSummaryBuilder(),
            timeline_builder=TimelineViewBuilder(),
        )
    )

    def build(
        self,
        *,
        runtime_result: dict[str, Any],
        events: list[dict[str, Any]],
        context_view: dict[str, Any] | None = None,
        governance_output: dict[str, Any] | None = None,
        worker_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        child_result = runtime_result.get("child_result", {})
        routing = runtime_result.get("routing", {})
        reconciliation = runtime_result.get("reconciliation", {}) or {}
        final_response = str(runtime_result.get("final_response", ""))

        operator_snapshot = self.operator_snapshot_builder.build(
            runtime_result=runtime_result,
        )
        dashboard_snapshot = self.dashboard_snapshot_builder.build(
            events=events,
            context_view=context_view,
            governance_output=governance_output,
            child_result=child_result,
            routing=routing,
            reconciliation=reconciliation,
            final_response=final_response,
            worker_payload=worker_payload,
        )

        return {
            "operator_snapshot": operator_snapshot,
            "dashboard_snapshot": dashboard_snapshot,
            "console_sections": self._console_sections(
                operator_snapshot=operator_snapshot,
                dashboard_snapshot=dashboard_snapshot,
            ),
        }

    @staticmethod
    def _console_sections(
        *,
        operator_snapshot: dict[str, Any],
        dashboard_snapshot: dict[str, Any],
    ) -> list[dict[str, Any]]:
        return [
            {
                "section": "coordination",
                "content": {
                    "lead_brain_for_action": operator_snapshot.get("lead_brain_for_action"),
                    "support_brain": operator_snapshot.get("support_brain"),
                    "hold_for_more_input": operator_snapshot.get("hold_for_more_input"),
                    "surface_disagreement_to_user": operator_snapshot.get("surface_disagreement_to_user"),
                },
            },
            {
                "section": "plurality",
                "content": {
                    "disagreement": dashboard_snapshot.get("disagreement", {}),
                    "reconciliation": dashboard_snapshot.get("reconciliation", {}),
                },
            },
            {
                "section": "integrity",
                "content": {
                    "integrity_flags": dashboard_snapshot.get("integrity_flags", []),
                    "governance": dashboard_snapshot.get("governance", {}),
                },
            },
            {
                "section": "timeline",
                "content": {
                    "events": dashboard_snapshot.get("timeline", []),
                },
            },
        ]
