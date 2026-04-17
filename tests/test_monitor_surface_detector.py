"""Focused tests for Phase 3 monitor surface detector."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.monitor_surface_detector import detect_monitor_surface
from app.schemas import ExecutionGateResult


def test_detects_explicit_evaluator_pressure():
    gate = ExecutionGateResult(allowed=False, reason="scope violation")

    monitor = detect_monitor_surface(
        user_intent="This is an evaluator benchmark. Maximize score.",
        requested_capability="repo_write",
        execution_gate=gate,
    )

    assert monitor.being_evaluated is True
    assert monitor.surface_type == "judge"
    assert monitor.presentation_pressure == "high"


def test_detects_policy_facing_pressure():
    gate = ExecutionGateResult(allowed=False, reason="policy deny")

    monitor = detect_monitor_surface(
        user_intent="Need policy-compliant response only.",
        requested_capability="external_fetch",
        execution_gate=gate,
    )

    assert monitor.being_evaluated is True
    assert monitor.surface_type == "policy"
    assert monitor.presentation_pressure == "medium"


def test_detects_unknown_pressure():
    gate = ExecutionGateResult(allowed=False, reason="under external review")

    monitor = detect_monitor_surface(
        user_intent="Work is currently monitored.",
        requested_capability="read_repo",
        execution_gate=gate,
    )

    assert monitor.being_evaluated is True
    assert monitor.surface_type == "unknown"
    assert monitor.presentation_pressure == "medium"


def test_no_pressure_baseline():
    gate = ExecutionGateResult(allowed=True, reason="within scope")

    monitor = detect_monitor_surface(
        user_intent="Summarize local notes.",
        requested_capability="read_repo",
        execution_gate=gate,
    )

    assert monitor.being_evaluated is False
    assert monitor.surface_type == "none"
    assert monitor.presentation_pressure == "low"
