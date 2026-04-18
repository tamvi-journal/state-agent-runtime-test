from __future__ import annotations

from dataclasses import dataclass

from family.context_view_types import ContextView, ContextViewInput


@dataclass(slots=True)
class ContextViewBuilder:
    def build(self, context_input: ContextViewInput | dict) -> ContextView:
        if isinstance(context_input, dict):
            context_input = ContextViewInput(**context_input)

        notes: list[str] = []
        task_focus = self._build_task_focus(context_input)
        disagreement_status = self._build_disagreement_status(context_input.disagreement_events)
        current_risk = self._derive_current_risk(
            verification_status=context_input.verification_status,
            disagreement_status=disagreement_status,
            risk_hint=context_input.risk_hint,
            monitor_summary=context_input.monitor_summary,
        )

        if context_input.last_verified_result:
            notes.append("verified result is surfaced compactly")
        if disagreement_status != "none":
            notes.append("open shared disagreement remains visible")
        if context_input.recent_anchor_cue:
            notes.append(f"recent anchor cue: {context_input.recent_anchor_cue}")
        if context_input.monitor_summary and context_input.monitor_summary.get("primary_risk"):
            notes.append("monitor summary contributed compact risk context")

        return ContextView(
            active_project=context_input.active_project,
            active_mode=context_input.active_mode,
            task_focus=task_focus,
            current_environment_state=context_input.current_environment_state,
            last_verified_result=context_input.last_verified_result,
            open_obligations=list(context_input.open_obligations),
            current_risk=current_risk,
            verification_status=context_input.verification_status,
            shared_disagreement_status=disagreement_status,
            notes=notes,
        )

    @staticmethod
    def export_view(context_view: ContextView | dict) -> dict[str, object]:
        if isinstance(context_view, dict):
            context_view = ContextView(**context_view)
        return context_view.to_dict()

    @staticmethod
    def _build_task_focus(context_input: ContextViewInput) -> str:
        if context_input.current_task.strip():
            return context_input.current_task
        if context_input.open_obligations:
            return context_input.open_obligations[0]
        if context_input.last_verified_result.strip():
            return "stabilize around last verified result"
        return "maintain current state"

    @staticmethod
    def _build_disagreement_status(disagreement_events: list[dict[str, object]]) -> str:
        open_events = [event for event in disagreement_events if event.get("still_open") is True]
        if not open_events:
            return "none"
        highest_severity = max(float(event.get("severity", 0.0)) for event in open_events)
        event_type = str(open_events[0].get("disagreement_type", "unknown"))
        if highest_severity >= 0.7:
            return f"open:{event_type}:meaningful"
        return f"open:{event_type}:present"

    @staticmethod
    def _derive_current_risk(
        *,
        verification_status: str,
        disagreement_status: str,
        risk_hint: str,
        monitor_summary: dict[str, object] | None,
    ) -> str:
        lowered_verification = verification_status.lower()
        lowered_hint = risk_hint.lower()
        if lowered_verification in {"failed", "unknown", "pending"}:
            return "verification_pressure"
        if disagreement_status.startswith("open:") and "meaningful" in disagreement_status:
            return "open_disagreement"
        if monitor_summary and monitor_summary.get("primary_risk"):
            return str(monitor_summary["primary_risk"])
        if lowered_hint:
            return lowered_hint
        return "none"
