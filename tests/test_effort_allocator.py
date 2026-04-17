from __future__ import annotations

from allocator.effort_allocator import EffortAllocator
from allocator.effort_schema import EffortInput


def test_allocator_routes_high_effort_for_high_stakes_architecture_turn() -> None:
    allocator = EffortAllocator()

    decision = allocator.route(
        EffortInput(
            task_type="architecture",
            domain="build/research",
            active_mode="build",
            mode_confidence=0.45,
            ambiguity_score=0.75,
            risk_score=0.40,
            stakes_signal=0.90,
            action_required=False,
            memory_commit_possible=True,
            disagreement_likelihood=0.70,
            cue_strength=0.10,
            verification_gap_estimate=0.20,
            high_risk_domain=False,
            unanswerable_likelihood=0.10,
        )
    )

    assert decision.effort_level == "high"
    assert decision.cognition_topology == "parallel_full"
    assert decision.monitor_intensity == "strict"
    assert decision.memory_commit_status == "allowed_after_verification"
    assert decision.disagreement_handling == "actively_hold_open"
    assert decision.reasoning_engine == "dual_pass"


def test_allocator_defaults_unknown_stakes_to_medium_not_low() -> None:
    allocator = EffortAllocator(default_unknown_stakes_to_medium=True)

    decision = allocator.route(
        EffortInput(
            task_type="chat",
            domain="generic",
            active_mode="care",
            mode_confidence=0.95,
            ambiguity_score=0.10,
            risk_score=0.10,
            stakes_signal=0.0,
            action_required=False,
            memory_commit_possible=False,
            disagreement_likelihood=0.10,
            cue_strength=0.20,
            verification_gap_estimate=0.10,
            high_risk_domain=False,
            unanswerable_likelihood=0.10,
        )
    )

    assert decision.effort_level == "medium"
    assert "stakes unclear -> precautionary default medium" in decision.rationale


def test_allocator_routes_low_effort_for_strong_cue_simple_turn_when_stakes_known_low() -> None:
    allocator = EffortAllocator(default_unknown_stakes_to_medium=True)

    decision = allocator.route(
        EffortInput(
            task_type="rewrite",
            domain="generic",
            active_mode="build",
            mode_confidence=0.95,
            ambiguity_score=0.05,
            risk_score=0.05,
            stakes_signal=0.10,
            action_required=False,
            memory_commit_possible=False,
            disagreement_likelihood=0.05,
            cue_strength=0.90,
            verification_gap_estimate=0.05,
            high_risk_domain=False,
            unanswerable_likelihood=0.05,
        )
    )

    assert decision.effort_level == "low"
    assert decision.cognition_topology == "single_brain"
    assert decision.monitor_intensity == "light"
    assert decision.verification_requirement == "optional"
    assert decision.memory_commit_status == "blocked"


def test_allocator_makes_verification_mandatory_when_action_required() -> None:
    allocator = EffortAllocator()

    decision = allocator.route(
        EffortInput(
            task_type="execution",
            domain="build/research",
            active_mode="execute",
            mode_confidence=0.80,
            ambiguity_score=0.20,
            risk_score=0.30,
            stakes_signal=0.40,
            action_required=True,
            memory_commit_possible=False,
            disagreement_likelihood=0.10,
            cue_strength=0.20,
            verification_gap_estimate=0.70,
            high_risk_domain=False,
            unanswerable_likelihood=0.10,
        )
    )

    assert decision.verification_requirement == "mandatory"
    assert decision.monitor_intensity in {"normal", "strict"}
