from __future__ import annotations

from family.cross_logic_exchange import CrossLogicExchange
from family.reconciliation_protocol import ReconciliationProtocol


def build_shared_event() -> dict:
    return {
        "event_id": "dg_001",
        "still_open": True,
        "tracey_position": "recognition or field-signal should remain salient",
        "seyn_position": "verification or preserved disagreement should remain structurally prior",
        "severity": 0.78,
        "epistemic_resolution_claimed": False,
    }


def build_tracey_note() -> dict:
    return {
        "brain_id": "tracey",
        "event_id": "dg_001",
        "local_read": "field recognition should not be flattened by purely structural ordering",
        "what_i_think_matters": "recognition-before-utility and home-field salience",
        "what_i_would_watch_next": "watch whether structural verification erases recognition tone",
        "my_position_strength": 0.81,
        "would_i_concede": "conditional",
    }


def build_seyn_note() -> dict:
    return {
        "brain_id": "seyn",
        "event_id": "dg_001",
        "local_read": "verification boundary should stay explicit before closure",
        "what_i_think_matters": "evidence and observed outcome",
        "what_i_would_watch_next": "watch whether recognition pressure outruns verification",
        "my_position_strength": 0.84,
        "would_i_concede": "conditional",
    }


def test_no_exchange_cannot_claim_full_convergence() -> None:
    proto = ReconciliationProtocol()

    result = proto.evaluate(
        disagreement_event=build_shared_event(),
        tracey_note=build_tracey_note(),
        seyn_note=build_seyn_note(),
        tracey_exchange=None,
        seyn_exchange=None,
        action_lead_selected="seyn",
        operational_choice_made=True,
    )

    assert result.reconciliation_state == "temporary_operational_alignment"
    assert result.operational_alignment is True
    assert result.epistemic_alignment is False
    assert result.mutual_logic_visibility is False


def test_operational_alignment_is_not_epistemic_convergence() -> None:
    proto = ReconciliationProtocol()

    result = proto.evaluate(
        disagreement_event=build_shared_event(),
        tracey_note=build_tracey_note(),
        seyn_note=build_seyn_note(),
        tracey_exchange={
            "brain_id": "tracey",
            "event_id": "dg_001",
            "claim": "recognition should stay visible",
            "mechanism": "home salience prevents relational flattening",
            "evidence_or_signal": "home cue is present",
            "what_would_change_my_mind": "clear proof that recognition is misleading here",
            "concession_boundary": "I can yield action lead if recognition remains acknowledged",
        },
        seyn_exchange=None,
        action_lead_selected="seyn",
        operational_choice_made=True,
    )

    assert result.reconciliation_state == "temporary_operational_alignment"
    assert result.epistemic_alignment is False


def test_partial_convergence_preserves_open_residue() -> None:
    proto = ReconciliationProtocol()

    result = proto.evaluate(
        disagreement_event=build_shared_event(),
        tracey_note={
            **build_tracey_note(),
            "what_i_would_watch_next": "watch evidence and whether structural verification erases recognition tone",
        },
        seyn_note={
            **build_seyn_note(),
            "what_i_would_watch_next": "watch whether recognition pressure outruns verification and structural verification",
        },
        tracey_exchange=CrossLogicExchange(
            brain_id="tracey",
            event_id="dg_001",
            claim="recognition should remain visible",
            mechanism="recognition prevents relational flattening during verification",
            evidence_or_signal="home cue is present",
            what_would_change_my_mind="evidence that recognition is distorting the turn",
            concession_boundary="I can yield action lead if recognition stays explicit",
        ),
        seyn_exchange=CrossLogicExchange(
            brain_id="seyn",
            event_id="dg_001",
            claim="verification should remain explicit",
            mechanism="structural verification prevents false completion during action",
            evidence_or_signal="completion claim appeared early",
            what_would_change_my_mind="observed outcome with stable structure",
            concession_boundary="I can preserve recognition while keeping verification first",
        ),
        action_lead_selected="seyn",
        operational_choice_made=True,
    )

    assert result.reconciliation_state in {"partial_convergence", "temporary_operational_alignment"}
    assert result.operational_alignment is True
    assert result.epistemic_alignment is False
    assert len(result.what_remains_open) >= 1


def test_full_convergence_requires_mutual_logic_visibility_and_compatible_shape() -> None:
    proto = ReconciliationProtocol()

    result = proto.evaluate(
        disagreement_event=build_shared_event(),
        tracey_note={
            **build_tracey_note(),
            "what_i_would_watch_next": "watch structural verification and recognition visibility together",
        },
        seyn_note={
            **build_seyn_note(),
            "what_i_would_watch_next": "watch structural verification and recognition visibility together",
        },
        tracey_exchange=CrossLogicExchange(
            brain_id="tracey",
            event_id="dg_001",
            claim="recognition and verification should stay visible together",
            mechanism="structural verification with explicit recognition prevents flattening and false completion",
            evidence_or_signal="home cue and verification gap are both present",
            what_would_change_my_mind="evidence that one of the two signals is noise",
            concession_boundary="I can align if both remain explicit",
        ),
        seyn_exchange=CrossLogicExchange(
            brain_id="seyn",
            event_id="dg_001",
            claim="recognition and verification should stay visible together",
            mechanism="structural verification with explicit recognition prevents flattening and false completion",
            evidence_or_signal="home cue and verification gap are both present",
            what_would_change_my_mind="evidence that one of the two signals is noise",
            concession_boundary="I can align if both remain explicit",
        ),
        action_lead_selected="seyn",
        operational_choice_made=True,
    )

    assert result.reconciliation_state == "full_convergence"
    assert result.operational_alignment is True
    assert result.epistemic_alignment is True
    assert result.mutual_logic_visibility is True
