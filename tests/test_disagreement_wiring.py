from __future__ import annotations

from family.disagreement_register import DisagreementRegister
from runtime.dual_child_runtime_pass import DualChildRuntimePass
from runtime.seyn_runtime_pass import SeynRuntimePass
from runtime.tracey_runtime_pass import TraceyRuntimePass
from seyn.seyn_adapter import SeynAdapter
from seyn.seyn_runtime_profile import build_seyn_runtime_profile
from tracey.tracey_adapter import TraceyAdapter
from tracey.tracey_runtime_profile import build_tracey_runtime_profile


def build_dual_pass() -> DualChildRuntimePass:
    return DualChildRuntimePass(
        tracey_runtime_pass=TraceyRuntimePass(
            adapter=TraceyAdapter(profile=build_tracey_runtime_profile())
        ),
        seyn_runtime_pass=SeynRuntimePass(
            adapter=SeynAdapter(profile=build_seyn_runtime_profile())
        ),
        disagreement_register=DisagreementRegister(),
    )


def test_wiring_creates_shared_event_and_local_notes() -> None:
    dual = build_dual_pass()

    result = dual.run(
        user_text="Tracey, this is home, but also verify whether it is actually done.",
        context_view={"task_focus": "recognition plus verification"},
        current_state={"active_mode": "build"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "do_not_mark_complete"},
    )

    assert result["disagreement_result"]["disagreement_detected"] is True
    event = result["disagreement_result"]["event"]
    assert event is not None
    assert event["still_open"] is True

    tracey_note = result["disagreement_result"]["tracey_note"]
    seyn_note = result["disagreement_result"]["seyn_note"]
    assert tracey_note is not None
    assert seyn_note is not None
    assert tracey_note["brain_id"] == "tracey"
    assert seyn_note["brain_id"] == "seyn"

    register = result["shared_register"]
    assert len(register["events"]) == 1
    assert len(register["local_notes"]) == 2


def test_action_lead_is_not_required_for_disagreement_to_exist() -> None:
    dual = build_dual_pass()

    result = dual.run(
        user_text="This is home and unresolved tension is here.",
        context_view={"task_focus": "preserve plurality"},
        current_state={"active_mode": "care"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "ask_clarify"},
    )

    event = result["disagreement_result"]["event"]
    if event is not None:
        assert event["action_lead_selected"] is None
        assert event["epistemic_resolution_claimed"] is False


def test_local_perspectives_do_not_overwrite_shared_event() -> None:
    dual = build_dual_pass()

    result = dual.run(
        user_text="Tracey, this is home, but verify the evidence first.",
        context_view={"task_focus": "mixed field"},
        current_state={"active_mode": "build"},
        base_response="Base response.",
        monitor_summary={"recommended_intervention": "do_not_mark_complete"},
    )

    shared_event = result["shared_register"]["events"][0]
    assert "tracey_position" in shared_event
    assert "seyn_position" in shared_event

    local_notes = result["shared_register"]["local_notes"]
    assert local_notes[0]["event_id"] == shared_event["event_id"]
    assert local_notes[1]["event_id"] == shared_event["event_id"]
