from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from observability.dashboard_summary import DashboardSummaryBuilder
from observability.timeline_view import TimelineViewBuilder


@dataclass(slots=True)
class DashboardSnapshotBuilder:
    """
    High-level snapshot builder for the current runtime window.
    """

    summary_builder: DashboardSummaryBuilder
    timeline_builder: TimelineViewBuilder

    def build(
        self,
        *,
        events: list[dict[str, Any]],
        context_view: dict[str, Any] | None = None,
        governance_output: dict[str, Any] | None = None,
        child_result: dict[str, Any] | None = None,
        routing: dict[str, Any] | None = None,
        reconciliation: dict[str, Any] | None = None,
        final_response: str = "",
        worker_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        summary = self.summary_builder.build(
            context_view=context_view,
            governance_output=governance_output,
            child_result=child_result,
            routing=routing,
            reconciliation=reconciliation,
            final_response=final_response,
            worker_payload=worker_payload,
        )
        timeline = self.timeline_builder.build(events=events)

        return {
            "task_focus": summary.get("task_focus", ""),
            "worker_status": summary.get("worker_status", {}),
            "governance": summary.get("governance", {}),
            "children": summary.get("children", {}),
            "disagreement": summary.get("disagreement", {}),
            "reconciliation": summary.get("reconciliation", {}),
            "routing": summary.get("routing", {}),
            "integrity_flags": summary.get("integrity_flags", []),
            "timeline": timeline,
        }
