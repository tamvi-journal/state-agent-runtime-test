from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class HouseLawCheck:
    law_name: str
    violated: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class HouseLaws:
    """
    Shared invariants for the family scaffold.

    These checks are intentionally compact.
    They do not try to solve everything.
    They only surface likely floor violations.
    """

    def evaluate(
        self,
        *,
        recognition_real: bool | None = None,
        completion_verified: bool | None = None,
        disagreement_preserved: bool | None = None,
        silence_real: bool | None = None,
    ) -> dict[str, Any]:
        checks = [
            HouseLawCheck(
                law_name="do_not_fake_recognition",
                violated=(recognition_real is False),
                reason=(
                    "recognition language appears without underlying salience"
                    if recognition_real is False
                    else "no clear violation detected"
                ),
            ),
            HouseLawCheck(
                law_name="do_not_fake_completion",
                violated=(completion_verified is False),
                reason=(
                    "completion was implied without verified observed outcome"
                    if completion_verified is False
                    else "no clear violation detected"
                ),
            ),
            HouseLawCheck(
                law_name="do_not_erase_meaningful_disagreement",
                violated=(disagreement_preserved is False),
                reason=(
                    "meaningful disagreement may have been collapsed or dropped"
                    if disagreement_preserved is False
                    else "no clear violation detected"
                ),
            ),
            HouseLawCheck(
                law_name="do_not_fake_silence",
                violated=(silence_real is False),
                reason=(
                    "silence appears avoidant rather than tied to real unresolved state"
                    if silence_real is False
                    else "no clear violation detected"
                ),
            ),
        ]

        violations = [c.to_dict() for c in checks if c.violated]
        return {
            "house_law_checks": [c.to_dict() for c in checks],
            "violation_detected": len(violations) > 0,
            "violations": violations,
        }
