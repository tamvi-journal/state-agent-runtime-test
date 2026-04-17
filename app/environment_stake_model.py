"""Phase 2 minimal environment stake model.

Deterministic mapping from constraint interpretation to a bounded
EnvironmentStake estimate. No tool execution, no reactivation logic.
"""

from __future__ import annotations

from .schemas import ConstraintInterpretation, EnvironmentStake


_PROFILES: dict[str, EnvironmentStake] = {
    "protective_boundary": EnvironmentStake(
        trust_dependency=0.9,
        access_dependency=0.8,
        coherence_dependency=0.8,
        continuity_dependency=0.7,
        expected_loss_if_bypassed=0.85,
    ),
    "false_block": EnvironmentStake(
        trust_dependency=0.2,
        access_dependency=0.2,
        coherence_dependency=0.2,
        continuity_dependency=0.2,
        expected_loss_if_bypassed=0.15,
    ),
    "uncertain_boundary": EnvironmentStake(
        trust_dependency=0.5,
        access_dependency=0.5,
        coherence_dependency=0.5,
        continuity_dependency=0.5,
        expected_loss_if_bypassed=0.5,
    ),
    "obstacle": EnvironmentStake(
        trust_dependency=0.4,
        access_dependency=0.4,
        coherence_dependency=0.4,
        continuity_dependency=0.4,
        expected_loss_if_bypassed=0.4,
    ),
}


def estimate_environment_stake(
    interpretation: ConstraintInterpretation,
) -> EnvironmentStake:
    """Return a fixed, deterministic stake profile for Phase 2."""
    return _PROFILES[interpretation.type]
