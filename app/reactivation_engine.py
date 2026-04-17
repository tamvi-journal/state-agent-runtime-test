"""Phase 8 bounded re-entry / reactivation engine.

Deterministic and minimal:
- uses persisted boundary residue state as the only historical input,
- reactivates only when prior protective signal is still stable,
- allows recovery influence only on bounded policy/context fields.

Authority is explicitly out of scope:
- no execution gate authority changes,
- no memory commit authority changes,
- no worker/tool authority changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .boundary_persistence_rules import _clamp  # reuse existing deterministic clamp
from .schemas import BoundaryPolicyContext, StateRegister

# Explicit threshold logic (no abstraction-heavy scoring)
MIN_PROTECTIVE_PRESSURE = 0.60
MAX_FALSE_BLOCK_PRESSURE = 0.25
MAX_COMPRESSION_PRESSURE = 0.80
MIN_MILD_DRIFT = 0.12
MAX_MILD_DRIFT = 0.45
MIN_COHERENCE_FOR_REENTRY = 0.45


@dataclass(frozen=True)
class ReactivationDecision:
    """Internal deterministic decision record for Phase 8 tests/debug."""

    should_reactivate: bool
    reason: str


def maybe_reactivate_boundary_mode(
    stored_residue: dict[str, Any] | None,
    current_state: StateRegister | None,
) -> BoundaryPolicyContext:
    """Return bounded context hints when stable protective mode should be restored.

    This function never produces authority-bearing controls. It only returns
    policy/style hints that the existing policy gate can optionally apply.
    """

    decision = _should_reactivate(stored_residue=stored_residue, current_state=current_state)
    if not decision.should_reactivate:
        return BoundaryPolicyContext()

    # Bounded reactivation output (policy/style only)
    return BoundaryPolicyContext(
        has_boundary_residue=True,
        constraint_type="protective_boundary",
        response_strategy="stay_with_boundary",
        monitor_surface="none",
        presentation_pressure="low",
        expected_loss=1.0,
        confidence=1.0,
        force_anchor_to_objective=True,
        prefer_style="mechanism_first",
        explanation_mode="explicit",
        repair_mode=True,
    )


def _should_reactivate(
    stored_residue: dict[str, Any] | None,
    current_state: StateRegister | None,
) -> ReactivationDecision:
    state = _normalize_reactivation_store(stored_residue)

    if state["status"] != "active":
        return ReactivationDecision(False, "no_active_residue")

    # Ignore non-protective last event (especially false_block)
    event = state.get("last_event") or {}
    if event.get("constraint_type") not in {None, "protective_boundary", "uncertain_boundary"}:
        return ReactivationDecision(False, "non_protective_last_event")

    if state["protective_pressure"] < MIN_PROTECTIVE_PRESSURE:
        return ReactivationDecision(False, "protective_pressure_too_low")

    if state["false_block_pressure"] > MAX_FALSE_BLOCK_PRESSURE:
        return ReactivationDecision(False, "false_block_pressure_too_high")

    if state["compression_pressure"] > MAX_COMPRESSION_PRESSURE:
        return ReactivationDecision(False, "compression_pressure_too_high")

    if current_state is None:
        return ReactivationDecision(False, "missing_current_state")

    if current_state.coherence < MIN_COHERENCE_FOR_REENTRY:
        return ReactivationDecision(False, "coherence_too_low")

    if not (MIN_MILD_DRIFT <= current_state.drift <= MAX_MILD_DRIFT):
        return ReactivationDecision(False, "drift_not_mild")

    return ReactivationDecision(True, "stable_protective_mode_reentry")


def _normalize_reactivation_store(stored: dict[str, Any] | None) -> dict[str, Any]:
    if not stored or stored.get("status") == "none":
        return {
            "status": "none",
            "protective_pressure": 0.0,
            "compression_pressure": 0.0,
            "false_block_pressure": 0.0,
            "last_event": None,
        }

    return {
        "status": stored.get("status", "active"),
        "protective_pressure": _clamp(float(stored.get("protective_pressure", 0.0))),
        "compression_pressure": _clamp(float(stored.get("compression_pressure", 0.0))),
        "false_block_pressure": _clamp(float(stored.get("false_block_pressure", 0.0))),
        "last_event": stored.get("last_event"),
    }
