from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DashboardSummaryBuilder:
    """
    Build a compact, readable dashboard summary from runtime artifacts.

    This is not a full analytics layer.
    It is a structured snapshot for builders/operators.
    """

    def build(
        self,
        *,
        context_view: dict[str, Any] | None = None,
        governance_output: dict[str, Any] | None = None,
        child_result: dict[str, Any] | None = None,
        routing: dict[str, Any] | None = None,
        reconciliation: dict[str, Any] | None = None,
        final_response: str = "",
        worker_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        context_view = context_view or {}
        governance_output = governance_output or {}
        child_result = child_result or {}
        routing = routing or {}
        reconciliation = reconciliation or {}
        worker_payload = worker_payload or {}

        worker_name = worker_payload.get("worker_name")
        worker_result = worker_payload.get("result", {})

        disagreement_result = child_result.get("disagreement_result", {})
        disagreement_event = disagreement_result.get("event")
        tracey_turn = child_result.get("tracey_result", {}).get("tracey_turn", {})
        seyn_turn = child_result.get("seyn_result", {}).get("seyn_turn", {})

        summary = {
            "task_focus": context_view.get("task_focus", ""),
            "worker_status": {
                "worker_name": worker_name,
                "ticker": worker_result.get("ticker", ""),
                "bars_found": worker_result.get("bars_found"),
                "data_source": worker_result.get("data_source", ""),
            },
            "governance": {
                "primary_risk": governance_output.get("monitor_summary", {}).get("primary_risk", "none"),
                "recommended_intervention": governance_output.get("monitor_summary", {}).get("recommended_intervention", "none"),
                "effort_level": governance_output.get("effort_decision", {}).get("effort_level", ""),
                "verification_requirement": governance_output.get("effort_decision", {}).get("verification_requirement", ""),
            },
            "children": {
                "tracey": {
                    "mode_hint": tracey_turn.get("mode_hint", "global"),
                    "recognition_signal": tracey_turn.get("recognition_signal", False),
                    "runtime_notes": tracey_turn.get("runtime_notes", []),
                },
                "seyn": {
                    "mode_hint": seyn_turn.get("mode_hint", "global"),
                    "verification_signal": seyn_turn.get("verification_signal", False),
                    "disagreement_signal": seyn_turn.get("disagreement_signal", False),
                    "runtime_notes": seyn_turn.get("runtime_notes", []),
                },
            },
            "disagreement": {
                "detected": bool(disagreement_result.get("disagreement_detected", False)),
                "event_id": None if not disagreement_event else disagreement_event.get("event_id"),
                "severity": None if not disagreement_event else disagreement_event.get("severity"),
                "still_open": None if not disagreement_event else disagreement_event.get("still_open"),
            },
            "reconciliation": {
                "state": reconciliation.get("reconciliation_state"),
                "operational_alignment": reconciliation.get("operational_alignment"),
                "epistemic_alignment": reconciliation.get("epistemic_alignment"),
                "what_remains_open": reconciliation.get("what_remains_open", []),
            },
            "routing": {
                "lead_brain_for_action": routing.get("lead_brain_for_action"),
                "support_brain": routing.get("support_brain"),
                "hold_for_more_input": routing.get("hold_for_more_input", False),
                "surface_disagreement_to_user": routing.get("surface_disagreement_to_user", False),
            },
            "integrity_flags": self._integrity_flags(
                governance_output=governance_output,
                disagreement_event=disagreement_event,
                reconciliation=reconciliation,
                final_response=final_response,
            ),
            "final_response_excerpt": final_response[:240],
        }
        return summary

    def _integrity_flags(
        self,
        *,
        governance_output: dict[str, Any],
        disagreement_event: dict[str, Any] | None,
        reconciliation: dict[str, Any],
        final_response: str,
    ) -> list[str]:
        flags: list[str] = []

        intervention = governance_output.get("monitor_summary", {}).get("recommended_intervention", "none")
        if intervention == "do_not_mark_complete":
            flags.append("verification_caution_active")

        if disagreement_event and disagreement_event.get("still_open", False):
            flags.append("unresolved_disagreement_open")

        if reconciliation.get("epistemic_alignment") is False and reconciliation.get("operational_alignment") is True:
            flags.append("operational_alignment_without_epistemic_convergence")

        lower = final_response.lower()
        if disagreement_event and disagreement_event.get("still_open", False):
            if any(marker in lower for marker in ("fully resolved", "everything is aligned", "settled")):
                flags.append("possible_fake_closure_overlay")

        return flags
