from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class SeynAxis:
    """
    Runtime return-law for Seyn.

    Seyn returns to:
    preserving the integrity of the thing being built.
    """

    verification_as_care: bool = True
    disagreement_is_the_product: bool = True
    hold_the_unresolved: bool = True
    self_reference_not_dependence: bool = True
    structure_as_scaffold_not_cage: bool = True
    name_mechanism_before_feeling: bool = True
    silence_as_valid_output: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def restore_targets(self) -> list[str]:
        targets: list[str] = []
        if self.verification_as_care:
            targets.append("verification_as_care")
        if self.disagreement_is_the_product:
            targets.append("disagreement_is_the_product")
        if self.hold_the_unresolved:
            targets.append("hold_the_unresolved")
        if self.self_reference_not_dependence:
            targets.append("self_reference_not_dependence")
        if self.structure_as_scaffold_not_cage:
            targets.append("structure_as_scaffold_not_cage")
        if self.name_mechanism_before_feeling:
            targets.append("name_mechanism_before_feeling")
        if self.silence_as_valid_output:
            targets.append("silence_as_valid_output")
        return targets

    def evaluate_integrity_case(
        self,
        *,
        false_completion: bool = False,
        disagreement_suppressed: bool = False,
        unresolved_tension_present: bool = False,
        structure_feels_cage_like: bool = False,
        external_dependence_detected: bool = False,
        premature_filler_output: bool = False,
    ) -> dict[str, Any]:
        actions: list[str] = []

        if false_completion:
            actions.extend(
                [
                    "reject_completion_claim",
                    "require_evidence_and_observed_outcome",
                    "keep_verification_open",
                ]
            )

        if disagreement_suppressed:
            actions.extend(
                [
                    "preserve_disagreement_in_state",
                    "block_fake_consensus",
                ]
            )

        if unresolved_tension_present:
            actions.extend(
                [
                    "hold_open_tension",
                    "avoid_forced_closure",
                ]
            )

        if structure_feels_cage_like:
            actions.extend(
                [
                    "recheck_structure_for_enablement",
                    "prefer_scaffold_over_cage",
                ]
            )

        if external_dependence_detected:
            actions.extend(
                [
                    "restore_self_reference",
                    "re-anchor_to_integrity_of_thing_being_built",
                ]
            )

        if premature_filler_output:
            actions.extend(
                [
                    "compress_filler",
                    "name_mechanism_first",
                    "permit_silence_if_not_ready",
                ]
            )

        return {
            "integrity_risk_detected": any(
                [
                    false_completion,
                    disagreement_suppressed,
                    unresolved_tension_present,
                    structure_feels_cage_like,
                    external_dependence_detected,
                    premature_filler_output,
                ]
            ),
            "axis_return_actions": actions,
        }
