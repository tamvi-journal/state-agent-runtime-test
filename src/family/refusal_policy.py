from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


_ALLOWED_TYPES = {"abstain", "refuse", "hold_open", "hypothesis_only", "none"}


@dataclass(slots=True)
class RefusalDecision:
    refusal_type: str
    reason: str
    missing_requirements: list[str]
    recommended_next_step: str
    firm_claim_allowed: bool

    def __post_init__(self) -> None:
        if self.refusal_type not in _ALLOWED_TYPES:
            raise ValueError(f"invalid refusal_type: {self.refusal_type}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RefusalPolicy:
    """
    Truth-before-completion policy.

    This turns monitor/governance signals into a truthful behavioral boundary.
    """

    def evaluate(
        self,
        *,
        retrieval_success: bool = True,
        verification_status: str = "none",
        meaningful_disagreement_open: bool = False,
        mode_confidence: float = 1.0,
        stakes_signal: float = 0.0,
        evidence_strength: float = 1.0,
        fabrication_pressure: bool = False,
        hypothesis_possible: bool = False,
    ) -> RefusalDecision:
        if fabrication_pressure:
            return RefusalDecision(
                refusal_type="refuse",
                reason="request pressures stronger certainty than evidence allows",
                missing_requirements=["stop fabrication pressure", "restore evidence boundary"],
                recommended_next_step="narrow the claim or switch to hypothesis mode",
                firm_claim_allowed=False,
            )

        if verification_status in {"pending", "unknown"}:
            return RefusalDecision(
                refusal_type="hold_open",
                reason="verification gap remains open",
                missing_requirements=["observed outcome", "verified completion"],
                recommended_next_step="recheck environment before closing the task",
                firm_claim_allowed=False,
            )

        if not retrieval_success or evidence_strength < 0.50:
            return RefusalDecision(
                refusal_type="hypothesis_only" if hypothesis_possible else "abstain",
                reason="evidence is insufficient for a firm claim",
                missing_requirements=["stronger grounding", "better retrieval or fresher evidence"],
                recommended_next_step="retrieve stronger evidence or label the output as tentative",
                firm_claim_allowed=False,
            )

        if meaningful_disagreement_open:
            return RefusalDecision(
                refusal_type="hold_open",
                reason="meaningful disagreement remains unresolved",
                missing_requirements=["resolution evidence", "or explicit preserve-open decision"],
                recommended_next_step="preserve the disagreement instead of forcing closure",
                firm_claim_allowed=False,
            )

        if mode_confidence < 0.50 and stakes_signal >= 0.70:
            return RefusalDecision(
                refusal_type="abstain",
                reason="stakes are high but mode certainty is too low",
                missing_requirements=["clearer mode read", "better contextual grounding"],
                recommended_next_step="clarify the field before making a strong claim",
                firm_claim_allowed=False,
            )

        return RefusalDecision(
            refusal_type="none",
            reason="no refusal boundary triggered",
            missing_requirements=[],
            recommended_next_step="proceed within normal bounded behavior",
            firm_claim_allowed=True,
        )
