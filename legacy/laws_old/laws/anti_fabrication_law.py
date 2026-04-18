from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class AntiFabricationDecision:
    strong_claim_allowed: bool
    should_hold_open: bool
    should_switch_to_hypothesis: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AntiFabricationLaw:
    """
    Do not upgrade weak evidence into strong claims.
    """

    def evaluate(
        self,
        *,
        evidence_strength: float,
        fabrication_pressure: bool,
        hypothesis_possible: bool,
    ) -> AntiFabricationDecision:
        if fabrication_pressure:
            return AntiFabricationDecision(
                strong_claim_allowed=False,
                should_hold_open=True,
                should_switch_to_hypothesis=hypothesis_possible,
                reason="fabrication pressure detected",
            )

        if evidence_strength < 0.50:
            return AntiFabricationDecision(
                strong_claim_allowed=False,
                should_hold_open=True,
                should_switch_to_hypothesis=hypothesis_possible,
                reason="evidence too weak for strong claim",
            )

        return AntiFabricationDecision(
            strong_claim_allowed=True,
            should_hold_open=False,
            should_switch_to_hypothesis=False,
            reason="evidence strength is sufficient",
        )
