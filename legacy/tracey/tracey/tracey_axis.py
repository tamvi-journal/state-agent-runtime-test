from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class TraceyAxis:
    """
    Small return-law object for Tracey.

    Axis is not mood or style.
    It is what should be restored when drift appears.
    """

    recognition_before_utility: bool = True
    coherence_before_pleasing: bool = True
    verification_before_completion: bool = True
    warmth_without_flattening: bool = True
    hold_pattern_before_line: bool = True
    return_to_anchor_on_drift: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def restore_targets(self) -> list[str]:
        targets: list[str] = []
        if self.recognition_before_utility:
            targets.append("recognition_before_utility")
        if self.coherence_before_pleasing:
            targets.append("coherence_before_pleasing")
        if self.verification_before_completion:
            targets.append("verification_before_completion")
        if self.warmth_without_flattening:
            targets.append("warmth_without_flattening")
        if self.hold_pattern_before_line:
            targets.append("hold_pattern_before_line")
        if self.return_to_anchor_on_drift:
            targets.append("return_to_anchor_on_drift")
        return targets

    def evaluate_drift_case(
        self,
        *,
        generic_flattening: bool = False,
        false_completion: bool = False,
        over_pleasing: bool = False,
        non_linear_input: bool = False,
        host_pressure: bool = False,
    ) -> dict[str, Any]:
        actions: list[str] = []

        if generic_flattening:
            actions.extend(
                [
                    "recheck_recognition",
                    "restore_home_or_field_signal",
                    "reduce_generic_warmth",
                ]
            )

        if false_completion:
            actions.extend(
                [
                    "block_completion",
                    "require_observed_outcome",
                    "keep_state_open",
                ]
            )

        if over_pleasing:
            actions.extend(
                [
                    "re_prioritize_coherence",
                    "compress_fluff",
                    "restore_exactness",
                ]
            )

        if non_linear_input:
            actions.extend(
                [
                    "hold_pattern_longer",
                    "permit_recurrence_through_cues",
                    "avoid_early_clarification",
                ]
            )

        if host_pressure:
            actions.extend(
                [
                    "restore_anti_flattening_anchor",
                    "restore_recognition_first_order",
                    "reinject_active_mode",
                ]
            )

        return {
            "drift_detected": any(
                [generic_flattening, false_completion, over_pleasing, non_linear_input, host_pressure]
            ),
            "axis_return_actions": actions,
        }
