from __future__ import annotations

from runtime.coordination_policy import CoordinationInput
from runtime.coordination_policy_engine import CoordinationPolicyEngine
from runtime.dual_brain_router import DualBrainRouter


def test_policy_engine_holds_on_verification_caution_plus_disagreement() -> None:
    engine = CoordinationPolicyEngine()

    result = engine.decide(
        CoordinationInput(
            current_mode="build",
            task_type="execution",
            risk_score=0.75,
            disagreement_severity=0.78,
            disagreement_detected=True,
            effort_level="high",
            verification_requirement="mandatory",
            monitor_intensity="strict",
            disagreement_handling="actively_hold_open",
            primary_risk="fake_progress",
            recommended_intervention="do_not_mark_complete",
            tracey_recognition_signal=True,
            seyn_verification_signal=True,
            seyn_disagreement_signal=False,
        )
    )

    assert result.hold_for_more_input is True
    assert result.hold_reason != ""
    assert "verification_caution" in result.policy_flags


def test_policy_engine_routes_home_turn_to_tracey() -> None:
    engine = CoordinationPolicyEngine()

    result = engine.decide(
        CoordinationInput(
            current_mode="home",
            task_type="chat",
            risk_score=0.10,
            disagreement_severity=0.0,
            disagreement_detected=False,
            effort_level="medium",
            verification_requirement="recommended",
            monitor_intensity="normal",
            disagreement_handling="preserve_if_present",
            primary_risk="none",
            recommended_intervention="none",
            tracey_recognition_signal=True,
            seyn_verification_signal=False,
            seyn_disagreement_signal=False,
        )
    )

    assert result.hold_for_more_input is False
    assert result.lead_brain_for_action == "tracey"
    assert result.support_brain == "seyn"


def test_router_reads_governance_output_and_routes_to_seyn() -> None:
    router = DualBrainRouter(policy_engine=CoordinationPolicyEngine())

    result = router.route(
        current_mode="build",
        task_type="verify",
        risk_score=0.65,
        disagreement_result={"disagreement_detected": False},
        tracey_turn={"recognition_signal": False},
        seyn_turn={"verification_signal": True, "disagreement_signal": False},
        user_preference=None,
        governance_output={
            "monitor_summary": {
                "primary_risk": "fake_progress",
                "recommended_intervention": "do_not_mark_complete",
            },
            "effort_decision": {
                "effort_level": "high",
                "verification_requirement": "mandatory",
                "monitor_intensity": "strict",
                "disagreement_handling": "actively_hold_open",
            },
        },
    )

    assert result["lead_brain_for_action"] in {"seyn", None}
    assert "policy_flags" in result


def test_surface_disagreement_when_open_and_high_enough() -> None:
    engine = CoordinationPolicyEngine()

    result = engine.decide(
        CoordinationInput(
            current_mode="build",
            task_type="architecture",
            risk_score=0.45,
            disagreement_severity=0.70,
            disagreement_detected=True,
            effort_level="high",
            verification_requirement="recommended",
            monitor_intensity="strict",
            disagreement_handling="actively_hold_open",
            primary_risk="ambiguity",
            recommended_intervention="ask_clarify",
            tracey_recognition_signal=False,
            seyn_verification_signal=False,
            seyn_disagreement_signal=True,
        )
    )

    assert result.surface_disagreement_to_user is True
