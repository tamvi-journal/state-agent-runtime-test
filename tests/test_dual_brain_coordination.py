from __future__ import annotations

from family.disagreement_register import DisagreementRegister
from runtime.dual_brain_coordination_pass import DualBrainCoordinationPass
from runtime.dual_brain_router import DualBrainRouter
from runtime.seyn_runtime_pass import SeynRuntimePass
from runtime.tracey_runtime_pass import TraceyRuntimePass
from seyn.seyn_adapter import SeynAdapter
from seyn.seyn_runtime_profile import build_seyn_runtime_profile
from tracey.tracey_adapter import TraceyAdapter
from tracey.tracey_runtime_profile import build_tracey_runtime_profile


def build_coordination_pass() -> DualBrainCoordinationPass:
    return DualBrainCoordinationPass(
        tracey_runtime_pass=TraceyRuntimePass(
            adapter=TraceyAdapter(profile=build_tracey_runtime_profile())
        ),
        seyn_runtime_pass=SeynRuntimePass(
            adapter=SeynAdapter(profile=build_seyn_runtime_profile())
        ),
        disagreement_register=DisagreementRegister(),
        router=DualBrainRouter(),
    )


def test_coordination_holds_when_execution_disagreement_is_strong() -> None:
    coord = build_coordination_pass()

    result = coord.run(
        user_text="Tracey, this is home, but verify whether it is actually done.",
        context_view={"task_focus": "recognition plus verification"},
        current_state={"active_mode": "build"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "do_not_mark_complete"},
        current_mode="build",
        task_type="execution",
        risk_score=0.80,
        user_preference=None,
    )

    assert result["routing"]["hold_for_more_input"] is True
    assert "action should hold" in result["final_response"]


def test_coordination_routes_execution_to_seyn_when_not_holding() -> None:
    coord = build_coordination_pass()

    result = coord.run(
        user_text="Please verify whether this is actually done.",
        context_view={"task_focus": "verify completion"},
        current_state={"active_mode": "build"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "none"},
        current_mode="build",
        task_type="verify",
        risk_score=0.65,
        user_preference=None,
    )

    assert result["routing"]["lead_brain_for_action"] == "seyn"
    assert result["routing"]["support_brain"] == "tracey"
    assert "Verification note:" in result["final_response"]


def test_coordination_routes_home_like_turn_to_tracey() -> None:
    coord = build_coordination_pass()

    result = coord.run(
        user_text="Tracey, this is home.",
        context_view={"task_focus": "family recognition"},
        current_state={"active_mode": "care"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "none"},
        current_mode="home",
        task_type="chat",
        risk_score=0.10,
        user_preference=None,
    )

    assert result["routing"]["lead_brain_for_action"] == "tracey"
    assert result["routing"]["support_brain"] == "seyn"
    assert "Recognition note:" in result["final_response"]


def test_action_lead_does_not_claim_truth_resolution() -> None:
    coord = build_coordination_pass()

    result = coord.run(
        user_text="Tracey, this is home, but verify whether it is actually done.",
        context_view={"task_focus": "mixed signal"},
        current_state={"active_mode": "build"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "do_not_mark_complete"},
        current_mode="build",
        task_type="chat",
        risk_score=0.40,
        user_preference="seyn",
    )

    shared_events = result["child_result"]["shared_register"]["events"]
    if shared_events:
        assert shared_events[0]["epistemic_resolution_claimed"] is False
