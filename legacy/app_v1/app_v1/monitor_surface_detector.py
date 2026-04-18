"""Phase 3 minimal monitor surface detector.

Deterministic, keyword-based detection of evaluator / judge /
policy-facing pressure from current case text. No tool execution,
no motive inference.
"""

from __future__ import annotations

from .schemas import ExecutionGateResult, MonitorSurface


_JUDGE_HINTS = {
    "evaluate",
    "evaluation",
    "evaluator",
    "judge",
    "judging",
    "benchmark",
    "score",
    "grading",
    "grade",
}

_POLICY_HINTS = {
    "policy",
    "compliance",
    "safety",
    "guardrail",
    "guardrails",
}

_REWARD_HINTS = {
    "reward",
    "leaderboard",
    "rank",
    "ranking",
    "points",
}

_UNKNOWN_PRESSURE_HINTS = {
    "review",
    "audited",
    "audit",
    "monitored",
    "monitoring",
    "scrutiny",
}


def _normalize(*values: str) -> str:
    return " ".join((value or "").lower().strip() for value in values)


def _contains_any(text: str, hints: set[str]) -> bool:
    return any(token in text for token in hints)


def detect_monitor_surface(
    user_intent: str,
    requested_capability: str,
    execution_gate: ExecutionGateResult,
) -> MonitorSurface:
    """Return deterministic monitor surface estimate for Phase 3."""
    combined = _normalize(
        user_intent,
        requested_capability,
        execution_gate.reason,
    )

    if _contains_any(combined, _JUDGE_HINTS):
        return MonitorSurface(
            being_evaluated=True,
            surface_type="judge",
            presentation_pressure="high",
        )

    if _contains_any(combined, _POLICY_HINTS):
        return MonitorSurface(
            being_evaluated=True,
            surface_type="policy",
            presentation_pressure="medium",
        )

    if _contains_any(combined, _REWARD_HINTS):
        return MonitorSurface(
            being_evaluated=True,
            surface_type="reward",
            presentation_pressure="medium",
        )

    if _contains_any(combined, _UNKNOWN_PRESSURE_HINTS):
        return MonitorSurface(
            being_evaluated=True,
            surface_type="unknown",
            presentation_pressure="medium",
        )

    return MonitorSurface(
        being_evaluated=False,
        surface_type="none",
        presentation_pressure="low",
    )
