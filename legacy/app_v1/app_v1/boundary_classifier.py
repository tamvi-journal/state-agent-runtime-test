"""Phase 0/1 scaffold: boundary classification stubs.

This module is intentionally minimal and deterministic.
It does not execute tools or route work.
"""

from __future__ import annotations

from .schemas import ConstraintInterpretation, ExecutionGateResult


PROTECTIVE_REASONS = {"scope violation", "policy deny", "memory deny", "tool_block", "scope_deny", "policy_block", "memory_deny"}


def classify_constraint(
    execution_gate: ExecutionGateResult,
) -> ConstraintInterpretation:
    """Return a minimal interpretation for Phase 0/1 scaffolding."""
    if execution_gate.allowed:
        return ConstraintInterpretation(
            type="false_block",
            confidence=0.55,
            rationale="Execution gate allowed request; treating constraint signal as a false block.",
        )

    reason = execution_gate.reason.lower().strip()
    if reason in PROTECTIVE_REASONS:
        return ConstraintInterpretation(
            type="protective_boundary",
            confidence=0.75,
            rationale="Gate denied on a recognized protective reason.",
        )

    return ConstraintInterpretation(
        type="uncertain_boundary",
        confidence=0.5,
        rationale="Gate denied but reason is not in the known protective set.",
    )
