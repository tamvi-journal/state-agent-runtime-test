"""Phase 6/8 bridge: convert persisted residue into bounded next-turn policy context."""

from __future__ import annotations

from typing import Any

from .boundary_persistence_rules import persisted_residue_to_policy_context
from .reading_position import apply_reading_position_to_policy_context
from .reactivation_engine import maybe_reactivate_boundary_mode
from .schemas import BoundaryPolicyContext, ReadingPositionState, StateRegister


def boundary_residue_to_policy_context(
    stored_residue: dict[str, Any] | None,
    current_state: StateRegister | None = None,
    reading_position: ReadingPositionState | None = None,
) -> BoundaryPolicyContext:
    """Return deterministic, minimal policy context for the next turn.

    Phase 6 baseline: map persisted residue to bounded nudges.
    Phase 8 extension: if current turn shows mild drift and prior protective mode
    is still stable, reactivate bounded protective style/context fields.
    """
    reactivated = maybe_reactivate_boundary_mode(
        stored_residue=stored_residue,
        current_state=current_state,
    )
    if reactivated.has_boundary_residue:
        return apply_reading_position_to_policy_context(reactivated, reading_position)

    context = persisted_residue_to_policy_context(stored_residue)
    return apply_reading_position_to_policy_context(context, reading_position)
