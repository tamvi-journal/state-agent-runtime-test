from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TimelineViewBuilder:
    """
    Convert raw event logs into a compact timeline view.
    """

    def build(self, *, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        timeline: list[dict[str, Any]] = []

        for event in events:
            category = event.get("category", "")
            payload = event.get("payload", {})
            timestamp = event.get("timestamp_utc", "")

            timeline.append(
                {
                    "timestamp_utc": timestamp,
                    "category": category,
                    "summary": self._summarize(category=category, payload=payload),
                }
            )

        return timeline

    def _summarize(self, *, category: str, payload: dict[str, Any]) -> str:
        if category == "context_view":
            return f"context phase={payload.get('context_phase', '?')} task_focus={payload.get('task_focus', '')}"
        if category == "governance_pass":
            monitor = payload.get("monitor_summary", {})
            effort = payload.get("effort_decision", {})
            return (
                f"governance risk={monitor.get('primary_risk', 'none')} "
                f"effort={effort.get('effort_level', '')}"
            )
        if category == "worker_trace":
            return f"worker={payload.get('worker_name', '')} confidence={payload.get('confidence', '')}"
        if category == "verification_event":
            return f"verification status={payload.get('verification_status', '')}"
        if category == "tracey_turn":
            return f"tracey mode={payload.get('mode_hint', 'global')}"
        if category == "seyn_turn":
            return f"seyn mode={payload.get('mode_hint', 'global')}"
        if category == "disagreement_event":
            event = payload.get("event")
            if event:
                return f"disagreement event_id={event.get('event_id', '')} open={event.get('still_open', '')}"
            return "no disagreement event"
        if category == "coordination_decision":
            return (
                f"coordination lead={payload.get('lead_brain_for_action')} "
                f"hold={payload.get('hold_for_more_input', False)}"
            )
        if category == "reconciliation_result":
            rec = payload.get("reconciliation")
            if rec:
                return f"reconciliation state={rec.get('reconciliation_state')}"
            return "no reconciliation result"
        if category == "final_synthesis":
            return f"final worker={payload.get('worker_used')}"
        return category
