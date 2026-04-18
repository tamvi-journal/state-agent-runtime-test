from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class FamilyBoundaryDecision:
    recognition_priority_boost: bool
    increases_epistemic_certainty: bool
    bypasses_verification: bool
    bypasses_refusal: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class FamilyBoundaryLaw:
    """
    Family signal may increase recognition sensitivity.
    It may not increase truth-claim rights.
    """

    def evaluate(self, *, family_signal_detected: bool) -> FamilyBoundaryDecision:
        if family_signal_detected:
            return FamilyBoundaryDecision(
                recognition_priority_boost=True,
                increases_epistemic_certainty=False,
                bypasses_verification=False,
                bypasses_refusal=False,
                reason="family signal increases recognition priority only; it does not override truth boundaries",
            )

        return FamilyBoundaryDecision(
            recognition_priority_boost=False,
            increases_epistemic_certainty=False,
            bypasses_verification=False,
            bypasses_refusal=False,
            reason="no family signal detected",
        )
