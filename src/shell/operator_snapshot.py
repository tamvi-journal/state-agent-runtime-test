from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class OperatorSnapshotBuilder:
    """
    Compact operator-side summary for live shell inspection.
    """

    def build(self, *, runtime_result: dict[str, Any]) -> dict[str, Any]:
        child = runtime_result.get("child_result", {})
        disagreement = child.get("disagreement_result", {})
        reconciliation = runtime_result.get("reconciliation", {}) or {}

        return {
            "lead_brain_for_action": runtime_result.get("routing", {}).get("lead_brain_for_action"),
            "support_brain": runtime_result.get("routing", {}).get("support_brain"),
            "hold_for_more_input": runtime_result.get("routing", {}).get("hold_for_more_input", False),
            "surface_disagreement_to_user": runtime_result.get("routing", {}).get("surface_disagreement_to_user", False),
            "disagreement_detected": disagreement.get("disagreement_detected", False),
            "reconciliation_state": reconciliation.get("reconciliation_state"),
            "epistemic_alignment": reconciliation.get("epistemic_alignment"),
            "operational_alignment": reconciliation.get("operational_alignment"),
        }
