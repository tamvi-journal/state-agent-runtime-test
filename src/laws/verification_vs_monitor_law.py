from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class RoleBoundary:
    component: str
    primary_question: str
    may_block_progress: bool
    may_assert_grounding: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class VerificationVsMonitorLaw:
    """
    Clarifies the split:

    Verification:
    - asks whether data/result is grounded

    Monitor:
    - asks whether the system is allowed to proceed safely
    """

    def boundaries(self) -> dict[str, Any]:
        verification = RoleBoundary(
            component="verification",
            primary_question="is the data/result grounded or observed?",
            may_block_progress=False,
            may_assert_grounding=True,
        )
        monitor = RoleBoundary(
            component="monitor",
            primary_question="is the system allowed to proceed, hold, clarify, or refuse?",
            may_block_progress=True,
            may_assert_grounding=False,
        )
        return {
            "verification": verification.to_dict(),
            "monitor": monitor.to_dict(),
        }
