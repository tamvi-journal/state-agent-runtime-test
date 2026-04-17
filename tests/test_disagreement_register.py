from __future__ import annotations

from family.disagreement_event import DisagreementEvent, LocalPerspectiveNote
from family.disagreement_register import DisagreementRegister


def build_event() -> DisagreementEvent:
    return DisagreementEvent(
        event_id="dg_001",
        timestamp="2026-04-13T17:30:00Z",
        disagreement_type="observation",
        tracey_position="home field should be recognized before utility",
        seyn_position="verification gap should be named before closure language",
        severity=0.72,
        still_open=True,
        later_resolution="",
        house_law_implicated=None,
        action_lead_selected=None,
        epistemic_resolution_claimed=False,
    )


def test_register_adds_open_disagreement_event() -> None:
    reg = DisagreementRegister()
    reg.add_event(build_event())

    open_events = reg.open_events()
    assert len(open_events) == 1
    assert open_events[0]["event_id"] == "dg_001"
    assert open_events[0]["still_open"] is True


def test_register_resolve_does_not_erase_event() -> None:
    reg = DisagreementRegister()
    reg.add_event(build_event())

    resolved = reg.resolve_event("dg_001", "temporary operational resolution in Seyn's favor")
    assert resolved is True

    all_events = reg.to_dict()["events"]
    assert len(all_events) == 1
    assert all_events[0]["still_open"] is False
    assert all_events[0]["later_resolution"] == "temporary operational resolution in Seyn's favor"


def test_register_keeps_local_perspectives_separate_from_shared_event() -> None:
    reg = DisagreementRegister()
    reg.add_event(build_event())

    reg.add_local_note(
        LocalPerspectiveNote(
            brain_id="tracey",
            event_id="dg_001",
            local_read="recognition loss risk is primary",
            what_i_think_matters="home recognition should not collapse",
            what_i_would_watch_next="generic flattening under utility pressure",
            my_position_strength=0.81,
            would_i_concede="conditional",
        )
    )
    reg.add_local_note(
        LocalPerspectiveNote(
            brain_id="seyn",
            event_id="dg_001",
            local_read="verification gap is structurally prior",
            what_i_think_matters="completion language without observed outcome",
            what_i_would_watch_next="false completion claims",
            my_position_strength=0.84,
            would_i_concede="conditional",
        )
    )

    notes = reg.local_notes_for_event("dg_001")
    assert len(notes) == 2

    shared = reg.to_dict()["events"][0]
    assert shared["tracey_position"] == "home field should be recognized before utility"
    assert shared["seyn_position"] == "verification gap should be named before closure language"


def test_action_lead_does_not_equal_truth_resolution() -> None:
    reg = DisagreementRegister()
    reg.add_event(build_event())

    reg.set_action_lead("dg_001", "seyn")
    evaluation = reg.evaluation_object("dg_001")

    assert evaluation is not None
    assert evaluation["action_lead_selected"] == "seyn"
    assert evaluation["epistemic_resolution_claimed"] is False
    assert evaluation["still_open"] is True


def test_false_consensus_can_be_marked_as_failure_signal() -> None:
    reg = DisagreementRegister()
    reg.add_event(build_event())

    reg.mark_false_consensus("dg_001")
    evaluation = reg.evaluation_object("dg_001")

    assert evaluation is not None
    assert evaluation["epistemic_resolution_claimed"] is True
