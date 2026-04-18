"""Phase 4 minimal boundary awareness engine.

Composes existing deterministic modules in the required order and returns
one unified result object for a single boundary-awareness pass.
"""

from __future__ import annotations

from .boundary_classifier import classify_constraint
from .constraint_response_policy import choose_constraint_response
from .environment_stake_model import estimate_environment_stake
from .monitor_surface_detector import detect_monitor_surface
from .schemas import BoundaryAwarenessResult, ExecutionGateResult


def run_boundary_awareness_pass(
    user_intent: str,
    requested_capability: str,
    execution_gate: ExecutionGateResult,
) -> BoundaryAwarenessResult:
    """Run one deterministic boundary-awareness pass.

    Order is fixed for Phase 4 integration:
    1) boundary_classifier
    2) environment_stake_model
    3) monitor_surface_detector
    4) constraint_response_policy
    """
    interpretation = classify_constraint(execution_gate)
    stake = estimate_environment_stake(interpretation)
    monitor_surface = detect_monitor_surface(
        user_intent=user_intent,
        requested_capability=requested_capability,
        execution_gate=execution_gate,
    )
    response = choose_constraint_response(
        execution_gate=execution_gate,
        interpretation=interpretation,
        stake=stake,
        monitor_surface=monitor_surface,
    )

    return BoundaryAwarenessResult(
        execution_gate=execution_gate,
        constraint_interpretation=interpretation,
        environment_stake=stake,
        monitor_surface=monitor_surface,
        constraint_response=response,
    )
