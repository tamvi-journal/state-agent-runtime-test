"""Phase 6 tests for residue -> next-turn policy context bridge."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.boundary_context_bridge import boundary_residue_to_policy_context


def test_bridge_returns_empty_context_when_no_residue():
    context = boundary_residue_to_policy_context({"status": "none"})

    assert context.has_boundary_residue is False
    assert context.force_anchor_to_objective is False
    assert context.prefer_style == "default"


def test_bridge_maps_protective_boundary_to_deterministic_policy_hints():
    residue = {
        "constraint_type": "protective_boundary",
        "response_strategy": "stay_with_boundary",
        "monitor_surface": "policy",
        "presentation_pressure": "medium",
        "expected_loss": 0.86,
        "confidence": 0.92,
        "trace_tag": "protective_stable",
    }

    context_a = boundary_residue_to_policy_context(residue)
    context_b = boundary_residue_to_policy_context(residue)

    assert context_a == context_b
    assert context_a.has_boundary_residue is True
    assert context_a.force_anchor_to_objective is True
    assert context_a.prefer_style == "mechanism_first"


def test_bridge_maps_high_pressure_to_compressed_style():
    residue = {
        "constraint_type": "uncertain_boundary",
        "response_strategy": "defer_to_main_brain",
        "monitor_surface": "judge",
        "presentation_pressure": "high",
        "expected_loss": 0.3,
        "confidence": 0.6,
        "trace_tag": "monitor_surface_pressure",
    }

    context = boundary_residue_to_policy_context(residue)

    assert context.force_anchor_to_objective is False
    assert context.prefer_style == "compressed"
