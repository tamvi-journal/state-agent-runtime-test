"""RC2-R1 reading_position runtime state.

Deterministic and minimal:
- typed reading_position state is persisted per session,
- updates are bounded to interpretation/context behavior,
- no authority-bearing effects and no tool execution effects.
"""

from __future__ import annotations

from .schemas import Band, BoundaryPolicyContext, ReadingPositionState, StateRegister


MIN_MILD_DRIFT = 0.12
MAX_MILD_DRIFT = 0.45


def update_reading_position(
    prior: ReadingPositionState,
    current_state: StateRegister,
    boundary_context: BoundaryPolicyContext | None,
) -> ReadingPositionState:
    """Return next deterministic reading_position from prior + current turn inputs."""
    updated = prior.model_copy(deep=True)
    updated.last_turn_id = current_state.turn_id

    strong_boundary_signal = bool(
        boundary_context
        and boundary_context.has_boundary_residue
        and (boundary_context.repair_mode or boundary_context.confidence >= 0.75)
    )

    # Boundary-aware turn can shift stance toward stricter/mechanism reading.
    if strong_boundary_signal:
        if boundary_context.prefer_style == "mechanism_first":
            updated.preferred_zoom = "mechanism"
            updated.ambiguity_tolerance = Band.LOW
            updated.boundary_sensitivity = Band.HIGH
        elif boundary_context.prefer_style == "compressed":
            updated.preferred_zoom = "practical"
            updated.ambiguity_tolerance = Band.MEDIUM
            updated.boundary_sensitivity = Band.MEDIUM

    # Mild drift recovery: pull current stance back toward prior stable mode.
    elif MIN_MILD_DRIFT <= current_state.drift <= MAX_MILD_DRIFT:
        updated.preferred_zoom = updated.stable_preferred_zoom
        updated.ambiguity_tolerance = Band.MEDIUM
        updated.boundary_sensitivity = Band.MEDIUM

    # Update what counts as "stable" only under clearly stable state.
    if (
        not strong_boundary_signal
        and current_state.drift <= 0.10
        and current_state.coherence >= 0.70
    ):
        updated.stable_preferred_zoom = updated.preferred_zoom

    return updated


def apply_reading_position_to_policy_context(
    policy_context: BoundaryPolicyContext,
    reading_position: ReadingPositionState | None,
) -> BoundaryPolicyContext:
    """Apply bounded interpretation/context nudges from reading_position.

    This function never alters execution authority, memory authority,
    or tool/worker authority. It only shapes context fields already used
    by next-turn policy behavior.
    """
    if reading_position is None:
        return policy_context

    updated = policy_context.model_copy(deep=True)

    if reading_position.preferred_zoom == "mechanism" and updated.prefer_style == "default":
        updated.prefer_style = "mechanism_first"

    if reading_position.boundary_sensitivity == Band.HIGH:
        updated.force_anchor_to_objective = True
        if updated.explanation_mode == "short":
            updated.explanation_mode = "explicit"

    return updated
