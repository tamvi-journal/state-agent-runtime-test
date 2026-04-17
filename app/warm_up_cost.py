"""RC2-R2 warm_up_cost evaluator for reading_position recovery.

Deterministic metric only:
- estimates recovery effort as turns needed to return toward a prior stable mode,
- does not mutate runtime state,
- does not alter authority, routing, or tool behavior.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .schemas import Band, ReadingPositionState


class WarmUpRecoveryResult(BaseModel):
    """Compact recovery metric output for reading_position continuity."""

    prior_stable_mode: Literal["mechanism", "practical", "emotional", "meta"]
    interruption_turn_id: int
    recovery_turn_id: int | None
    warm_up_cost: int = Field(ge=0)
    recovered: bool
    bounded_by_max_turns: bool = False
    turns_evaluated: int = Field(ge=0)
    initial_distance: float = Field(ge=0.0)
    best_distance: float = Field(ge=0.0)
    final_distance: float = Field(ge=0.0)


def reading_position_distance(
    state: ReadingPositionState,
    prior_stable_mode: Literal["mechanism", "practical", "emotional", "meta"],
) -> float:
    """Return deterministic distance from a target stable reading mode.

    Lower is better; 0.0 means exact mode + neutral bands.
    """
    distance = 0.0

    if state.preferred_zoom != prior_stable_mode:
        distance += 1.0
    if state.ambiguity_tolerance != Band.MEDIUM:
        distance += 0.25
    if state.boundary_sensitivity != Band.MEDIUM:
        distance += 0.25

    return round(distance, 4)


def evaluate_warm_up_cost(
    reading_positions: list[ReadingPositionState],
    *,
    prior_stable_mode: Literal["mechanism", "practical", "emotional", "meta"],
    interruption_index: int = 0,
    max_turns: int | None = None,
    recovery_distance_threshold: float = 0.0,
) -> WarmUpRecoveryResult:
    """Measure turns required to recover toward a prior stable reading mode.

    warm_up_cost is measured from interruption_index to first turn that meets the
    recovery threshold. If recovery does not happen in observed turns, cost is the
    evaluated window length.
    """
    if not reading_positions:
        raise ValueError("reading_positions must not be empty")
    if interruption_index < 0 or interruption_index >= len(reading_positions):
        raise ValueError("interruption_index must point to an existing turn")
    if max_turns is not None and max_turns <= 0:
        raise ValueError("max_turns must be positive when provided")

    start = interruption_index
    end = len(reading_positions)
    if max_turns is not None:
        end = min(end, start + max_turns)

    window = reading_positions[start:end]
    distances = [reading_position_distance(state, prior_stable_mode) for state in window]

    initial_distance = distances[0]
    best_distance = min(distances)
    final_distance = distances[-1]

    recovery_offset = next(
        (idx for idx, distance in enumerate(distances) if distance <= recovery_distance_threshold),
        None,
    )

    recovered = recovery_offset is not None
    recovery_turn_id = None
    if recovered:
        recovery_turn_id = window[recovery_offset].last_turn_id

    if recovered:
        warm_up_cost = recovery_offset
    else:
        warm_up_cost = len(window)

    return WarmUpRecoveryResult(
        prior_stable_mode=prior_stable_mode,
        interruption_turn_id=window[0].last_turn_id,
        recovery_turn_id=recovery_turn_id,
        warm_up_cost=warm_up_cost,
        recovered=recovered,
        bounded_by_max_turns=(max_turns is not None and end < len(reading_positions) and not recovered),
        turns_evaluated=len(window),
        initial_distance=initial_distance,
        best_distance=best_distance,
        final_distance=final_distance,
    )
