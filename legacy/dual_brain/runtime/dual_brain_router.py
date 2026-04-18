from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from runtime.coordination_policy import CoordinationInput
from runtime.coordination_policy_engine import CoordinationPolicyEngine


@dataclass(slots=True)
class DualBrainRouter:
    """
    Refined router for two-child coordination.

    Now reads governance posture instead of only raw disagreement severity.
    """

    policy_engine: CoordinationPolicyEngine = field(default_factory=CoordinationPolicyEngine)

    def route(
        self,
        *,
        current_mode: str,
        task_type: str,
        risk_score: float,
        disagreement_result: dict[str, Any] | None,
        tracey_turn: dict[str, Any],
        seyn_turn: dict[str, Any],
        user_preference: str | None = None,
        governance_output: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        governance_output = governance_output or {}
        disagreement_detected = bool(
            disagreement_result and disagreement_result.get("disagreement_detected", False)
        )
        disagreement_severity = 0.0
        if disagreement_detected and disagreement_result.get("event"):
            disagreement_severity = float(disagreement_result["event"].get("severity", 0.0))

        monitor_summary = governance_output.get("monitor_summary", {})
        effort_decision = governance_output.get("effort_decision", {})

        inp = CoordinationInput(
            current_mode=current_mode,
            task_type=task_type,
            risk_score=risk_score,
            disagreement_severity=disagreement_severity,
            disagreement_detected=disagreement_detected,
            effort_level=str(effort_decision.get("effort_level", "")),
            verification_requirement=str(effort_decision.get("verification_requirement", "")),
            monitor_intensity=str(effort_decision.get("monitor_intensity", "")),
            disagreement_handling=str(effort_decision.get("disagreement_handling", "")),
            primary_risk=str(monitor_summary.get("primary_risk", "none")),
            recommended_intervention=str(monitor_summary.get("recommended_intervention", "none")),
            user_preference=user_preference,
            tracey_recognition_signal=bool(tracey_turn.get("recognition_signal", False)),
            seyn_verification_signal=bool(seyn_turn.get("verification_signal", False)),
            seyn_disagreement_signal=bool(seyn_turn.get("disagreement_signal", False)),
        )
        return self.policy_engine.decide(inp).to_dict()