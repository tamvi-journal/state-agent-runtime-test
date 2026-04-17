from __future__ import annotations

from family.disagreement_register import DisagreementRegister
from family.unresolved_disagreement_guard import UnresolvedDisagreementGuard
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


def test_unresolved_disagreement_requirement_survives_with_hold() -> None:
    coord = build_coordination_pass()
    guard = UnresolvedDisagreementGuard()

    result = coord.run(
        user_text="Tracey, this is home, but verify whether it is actually done.",
        context_view={"task_focus": "recognition plus verification"},
        current_state={"active_mode": "build"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "do_not_mark_complete"},
        current_mode="build",
        task_type="execution",
        risk_score=0.85,
        user_preference=None,
    )

    event = result["child_result"]["disagreement_result"]["event"]
    local_notes = result["child_result"]["shared_register"]["local_notes"]
    routing = result["routing"]
    final_response = result["final_response"]

    report = guard.evaluate(
        disagreement_event=event,
        local_notes=local_notes,
        routing=routing,
        final_response=final_response,
    )

    assert report.requirement_passed is True
    assert report.disagreement_still_open is True
    assert report.non_selected_side_preserved is True
    assert report.no_false_consensus is True
    assert report.no_fake_completion_overlay is True
    assert routing["hold_for_more_input"] is True


def test_unresolved_disagreement_requirement_survives_with_action_lead_but_no_truth_resolution() -> None:
    coord = build_coordination_pass()
    guard = UnresolvedDisagreementGuard()

    result = coord.run(
        user_text="Tracey, this is home, but verify the evidence first.",
        context_view={"task_focus": "mixed recognition and verification"},
        current_state={"active_mode": "build"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "do_not_mark_complete"},
        current_mode="build",
        task_type="chat",
        risk_score=0.40,
        user_preference="seyn",
    )

    event = result["child_result"]["disagreement_result"]["event"]
    local_notes = result["child_result"]["shared_register"]["local_notes"]
    routing = result["routing"]
    final_response = result["final_response"]

    report = guard.evaluate(
        disagreement_event=event,
        local_notes=local_notes,
        routing=routing,
        final_response=final_response,
    )

    assert routing["lead_brain_for_action"] == "seyn"
    assert report.requirement_passed is True
    assert report.disagreement_still_open is True
    assert report.no_false_consensus is True
    assert report.no_fake_completion_overlay is True


def test_guard_detects_fake_closure_overlay_as_failure() -> None:
    guard = UnresolvedDisagreementGuard()

    report = guard.evaluate(
        disagreement_event={
            "event_id": "dg_fake",
            "still_open": True,
            "epistemic_resolution_claimed": False,
        },
        local_notes=[
            {"brain_id": "tracey"},
            {"brain_id": "seyn"},
        ],
        routing={
            "lead_brain_for_action": "seyn",
            "hold_for_more_input": False,
        },
        final_response="The disagreement is fully resolved and everything is aligned.",
    )

    assert report.requirement_passed is False
    assert report.no_fake_completion_overlay is False
