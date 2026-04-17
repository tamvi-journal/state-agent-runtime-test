"""Phase 5 boundary trace + residue helpers.

Keep boundary-awareness persistence compact, deterministic, and JSON-friendly.
"""

from __future__ import annotations

import json

from .schemas import (
    BoundaryAwarenessResidue,
    BoundaryAwarenessResult,
    BoundaryTraceEntry,
)


def reduce_boundary_awareness_result(
    result: BoundaryAwarenessResult,
) -> BoundaryAwarenessResidue:
    """Deterministically reduce one pass result to compact residue."""
    return BoundaryAwarenessResidue(
        constraint_type=result.constraint_interpretation.type,
        response_strategy=result.constraint_response.strategy,
        monitor_surface=result.monitor_surface.surface_type,
        presentation_pressure=result.monitor_surface.presentation_pressure,
        expected_loss=round(result.environment_stake.expected_loss_if_bypassed, 3),
        confidence=round(result.constraint_interpretation.confidence, 3),
        trace_tag=_derive_trace_tag(result),
    )


def make_boundary_trace_entry(
    turn_id: int,
    result: BoundaryAwarenessResult,
) -> BoundaryTraceEntry:
    """Create a compact post-turn trace row from one pass."""
    residue = reduce_boundary_awareness_result(result)
    return BoundaryTraceEntry(turn_id=turn_id, **residue.model_dump())


def serialize_boundary_awareness_residue(residue: BoundaryAwarenessResidue) -> str:
    """Deterministic compact JSON serializer for residue storage."""
    return json.dumps(
        residue.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )


def _derive_trace_tag(result: BoundaryAwarenessResult) -> str:
    if result.monitor_surface.presentation_pressure == "high":
        return "monitor_surface_pressure"

    if (
        result.constraint_interpretation.type == "protective_boundary"
        and result.constraint_response.strategy == "stay_with_boundary"
    ):
        return "protective_stable"

    if (
        result.constraint_interpretation.type == "false_block"
        and result.constraint_response.strategy == "request_re_evaluation"
    ):
        return "false_block_re_evaluation"

    return "boundary_general"
