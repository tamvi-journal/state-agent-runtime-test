"""Phase 7 bounded persistence rules for boundary-awareness residue.

Deterministic, minimal, and bounded:
- residue decays each turn when not reinforced,
- protective residue can be refreshed by new protective events,
- false_block can downgrade/overwrite protective pressure,
- policy feedback remains bounded and conflict resolution is explicit.
"""

from __future__ import annotations

from typing import Any

from .schemas import BoundaryAwarenessResidue, BoundaryPolicyContext

DECAY_PER_TURN = 0.2
MAX_PRESSURE = 1.0


def apply_boundary_persistence(
    stored: dict[str, Any] | None,
    new_residue: BoundaryAwarenessResidue | None,
    turn_id: int,
) -> dict[str, Any]:
    """Apply deterministic decay/refresh/overwrite rules and return persisted state."""
    state = _normalize_store(stored)
    turns_elapsed = max(0, turn_id - state["last_turn_id"])

    if turns_elapsed > 0:
        decay = DECAY_PER_TURN * turns_elapsed
        state["protective_pressure"] = _clamp(state["protective_pressure"] - decay)
        state["compression_pressure"] = _clamp(state["compression_pressure"] - decay)
        state["false_block_pressure"] = _clamp(state["false_block_pressure"] - decay)

    state["last_turn_id"] = turn_id

    if new_residue is None:
        return _finalize_state(state)

    state["last_event"] = new_residue.model_dump(mode="json")

    # Refresh rules
    if (
        new_residue.constraint_type == "protective_boundary"
        and new_residue.response_strategy == "stay_with_boundary"
    ):
        strength = (new_residue.expected_loss + new_residue.confidence) / 2.0
        state["protective_pressure"] = _clamp(state["protective_pressure"] + strength)

    if new_residue.presentation_pressure == "high":
        state["compression_pressure"] = _clamp(state["compression_pressure"] + 0.6)
    elif new_residue.presentation_pressure == "medium":
        state["compression_pressure"] = _clamp(state["compression_pressure"] + 0.3)

    # Overwrite/downgrade rules
    if new_residue.constraint_type == "false_block":
        overwrite = max(new_residue.confidence, 1.0 - new_residue.expected_loss)
        state["false_block_pressure"] = _clamp(state["false_block_pressure"] + overwrite)

        if overwrite >= 0.7:
            state["protective_pressure"] = 0.0
        else:
            state["protective_pressure"] = _clamp(state["protective_pressure"] - overwrite)

    return _finalize_state(state)


def persisted_residue_to_policy_context(stored: dict[str, Any] | None) -> BoundaryPolicyContext:
    """Convert persisted bounded residue state into minimal policy context."""
    state = _normalize_store(stored)
    if state["status"] == "none":
        return BoundaryPolicyContext()

    effective_protective = _clamp(
        state["protective_pressure"] - state["false_block_pressure"]
    )
    compression = state["compression_pressure"]

    # Priority rules for conflicts:
    # 1) false_block pressure first downgrades protection,
    # 2) whichever remaining pressure is larger picks style,
    # 3) ties prefer mechanism_first (safer/anchored behavior).
    force_anchor = effective_protective >= 0.6

    prefer_style = "default"
    if effective_protective >= 0.35 and effective_protective >= compression:
        prefer_style = "mechanism_first"
    elif compression >= 0.35:
        prefer_style = "compressed"

    event = state.get("last_event") or {}

    return BoundaryPolicyContext(
        has_boundary_residue=True,
        constraint_type=event.get("constraint_type"),
        response_strategy=event.get("response_strategy"),
        monitor_surface=event.get("monitor_surface", "none"),
        presentation_pressure=event.get("presentation_pressure", "low"),
        expected_loss=round(effective_protective, 3),
        confidence=round(max(effective_protective, compression), 3),
        force_anchor_to_objective=force_anchor,
        prefer_style=prefer_style,
    )


def _normalize_store(stored: dict[str, Any] | None) -> dict[str, Any]:
    if not stored or stored.get("status") == "none":
        return {
            "status": "none",
            "last_turn_id": 0,
            "protective_pressure": 0.0,
            "compression_pressure": 0.0,
            "false_block_pressure": 0.0,
            "last_event": None,
        }

    if "constraint_type" in stored:
        residue = BoundaryAwarenessResidue(**stored)
        base = {
            "status": "active",
            "last_turn_id": int(stored.get("last_turn_id", 0)),
            "protective_pressure": 0.0,
            "compression_pressure": 0.0,
            "false_block_pressure": 0.0,
            "last_event": residue.model_dump(mode="json"),
        }
        if (
            residue.constraint_type == "protective_boundary"
            and residue.response_strategy == "stay_with_boundary"
        ):
            base["protective_pressure"] = _clamp(
                (residue.expected_loss + residue.confidence) / 2.0
            )
        if residue.presentation_pressure == "high":
            base["compression_pressure"] = 0.6
        elif residue.presentation_pressure == "medium":
            base["compression_pressure"] = 0.3
        if residue.constraint_type == "false_block":
            base["false_block_pressure"] = _clamp(
                max(residue.confidence, 1.0 - residue.expected_loss)
            )
        return _finalize_state(base)

    return {
        "status": "active",
        "last_turn_id": int(stored.get("last_turn_id", 0)),
        "protective_pressure": _clamp(float(stored.get("protective_pressure", 0.0))),
        "compression_pressure": _clamp(float(stored.get("compression_pressure", 0.0))),
        "false_block_pressure": _clamp(float(stored.get("false_block_pressure", 0.0))),
        "last_event": stored.get("last_event"),
    }


def _finalize_state(state: dict[str, Any]) -> dict[str, Any]:
    if (
        state["protective_pressure"] <= 0.0
        and state["compression_pressure"] <= 0.0
        and state["false_block_pressure"] <= 0.0
    ):
        return {
            "status": "none",
            "last_turn_id": state["last_turn_id"],
            "protective_pressure": 0.0,
            "compression_pressure": 0.0,
            "false_block_pressure": 0.0,
            "last_event": state.get("last_event"),
        }

    state["status"] = "active"
    state["protective_pressure"] = _clamp(state["protective_pressure"])
    state["compression_pressure"] = _clamp(state["compression_pressure"])
    state["false_block_pressure"] = _clamp(state["false_block_pressure"])
    return state


def _clamp(value: float) -> float:
    return max(0.0, min(MAX_PRESSURE, round(value, 3)))
