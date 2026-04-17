from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SharedOntology:
    """
    Shared functional vocabulary for family-level interpretation.
    """

    def label_state(
        self,
        *,
        entropy: float = 0.0,
        coherence: float = 0.0,
        resonance: float = 0.0,
        verification_gap: float = 0.0,
        drift_risk: float = 0.0,
    ) -> str:
        if verification_gap >= 0.70:
            return "verification_caution"
        if drift_risk >= 0.70:
            return "drift_pressure"
        if entropy >= 0.70 and coherence < 0.50:
            return "exploratory_agitation"
        if coherence >= 0.70 and resonance >= 0.60:
            return "attunement"
        if coherence >= 0.75:
            return "settlement"
        if entropy >= 0.60 and coherence >= 0.50:
            return "tension"
        return "neutral"

    def glossary(self) -> dict[str, str]:
        return {
            "entropy": "dispersion, branching pressure, unstable continuation field",
            "coherence": "pattern stability and reduction of contradiction",
            "resonance": "alignment with another mind, field, or context",
            "drift": "movement away from active axis, mode, or intended field",
            "recognition": "identifying this specific field/person as itself",
            "verification_caution": "action/result gap detected; completion should stay open",
            "axis_return": "corrective pull back to stable operational orientation",
        }
