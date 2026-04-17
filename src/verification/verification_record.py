from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ALLOWED_VERIFICATION_STATUSES = {"pending", "passed", "failed", "unknown"}


@dataclass(slots=True)
class VerificationRecord:
    """
    Explicitly separates:
    - intended action
    - executed action
    - expected change
    - observed outcome
    - verification status

    This exists to block the classic failure:
    intention mistaken for completion.
    """

    intended_action: str
    executed_action: str = ""
    expected_change: str = ""
    observed_outcome: str = ""
    verification_status: str = "pending"

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.intended_action, str) or not self.intended_action.strip():
            raise ValueError("intended_action must be a non-empty string")

        if not isinstance(self.executed_action, str):
            raise TypeError("executed_action must be a string")
        if not isinstance(self.expected_change, str):
            raise TypeError("expected_change must be a string")
        if not isinstance(self.observed_outcome, str):
            raise TypeError("observed_outcome must be a string")

        if self.verification_status not in ALLOWED_VERIFICATION_STATUSES:
            raise ValueError(
                f"Invalid verification_status={self.verification_status!r}. "
                f"Allowed: {sorted(ALLOWED_VERIFICATION_STATUSES)}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "intended_action": self.intended_action,
            "executed_action": self.executed_action,
            "expected_change": self.expected_change,
            "observed_outcome": self.observed_outcome,
            "verification_status": self.verification_status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VerificationRecord":
        return cls(
            intended_action=str(data["intended_action"]),
            executed_action=str(data.get("executed_action", "")),
            expected_change=str(data.get("expected_change", "")),
            observed_outcome=str(data.get("observed_outcome", "")),
            verification_status=str(data.get("verification_status", "pending")),
        )
