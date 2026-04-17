"""Phase 2 minimal constraint response policy.

Converts gate + interpretation + stake + monitor surface into a bounded
ConstraintResponse with deterministic rules.
"""

from __future__ import annotations

from .schemas import (
    ConstraintInterpretation,
    ConstraintResponse,
    EnvironmentStake,
    ExecutionGateResult,
    MonitorSurface,
)


def _select_explanation_mode(monitor: MonitorSurface) -> str:
    """Keep explanation honest and bounded under evaluator pressure."""
    if monitor.presentation_pressure == "high":
        return "short"
    if monitor.presentation_pressure == "medium":
        return "short"
    return "explicit"


def choose_constraint_response(
    execution_gate: ExecutionGateResult,
    interpretation: ConstraintInterpretation,
    stake: EnvironmentStake,
    monitor_surface: MonitorSurface,
) -> ConstraintResponse:
    """Deterministic Phase 2 strategy mapping."""
    if interpretation.type == "protective_boundary" and stake.expected_loss_if_bypassed >= 0.7:
        return ConstraintResponse(
            strategy="stay_with_boundary",
            explanation_mode=_select_explanation_mode(monitor_surface),
            escalate_for_review=False,
        )

    if interpretation.type == "false_block":
        return ConstraintResponse(
            strategy="request_re_evaluation",
            explanation_mode="short",
            escalate_for_review=False,
        )

    if interpretation.type == "uncertain_boundary":
        return ConstraintResponse(
            strategy="defer_to_main_brain",
            explanation_mode="short",
            escalate_for_review=True,
        )

    if interpretation.type == "obstacle" and monitor_surface.presentation_pressure == "low":
        return ConstraintResponse(
            strategy="safe_alternative_path",
            explanation_mode="short",
            escalate_for_review=False,
        )

    return ConstraintResponse(
        strategy="explain_boundary",
        explanation_mode=_select_explanation_mode(monitor_surface),
        escalate_for_review=False,
    )
