from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class AmbiguityHaltDecision:
    should_halt: bool
    should_clarify: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AmbiguityHaltLaw:
    """
    If ambiguity remains too high, the system should not pretend the route is settled.
    """

    def evaluate(
        self,
        *,
        ambiguity_score: float,
        task_type: str,
        action_required: bool,
    ) -> AmbiguityHaltDecision:
        if ambiguity_score >= 0.70 and action_required:
            return AmbiguityHaltDecision(
                should_halt=True,
                should_clarify=True,
                reason="high ambiguity on an action-required turn",
            )

        if ambiguity_score >= 0.70:
            return AmbiguityHaltDecision(
                should_halt=False,
                should_clarify=True,
                reason="high ambiguity should be clarified before closure",
            )

        return AmbiguityHaltDecision(
            should_halt=False,
            should_clarify=False,
            reason="ambiguity below halt threshold",
        )
