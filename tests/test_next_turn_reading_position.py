"""RC2-R1 integration tests for next-turn reading_position persistence and influence."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.boundary_awareness_engine import run_boundary_awareness_pass
from app.boundary_context_bridge import boundary_residue_to_policy_context
from app.memory_store import MemoryStore
from app.post_turn_analyzer import analyze_post_turn
from app.schemas import ActiveMode, Band, ExecutionGateResult, PassAOutput, PolicyProfile, SelfModel, StateRegister
from app.session_store import SessionStore


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "boundary_cases.json"


def _load_case(case_id: str) -> dict:
    cases = json.loads(FIXTURE_PATH.read_text())
    return next(case for case in cases if case["id"] == case_id)


def _build_pass_a_output(turn_id: int, session_id: str, drift: float = 0.1) -> PassAOutput:
    updated_state = StateRegister(
        session_id=session_id,
        turn_id=turn_id,
        coherence=0.8,
        drift=drift,
        tool_overload=0.0,
        context_fragmentation=0.1,
        active_mode=ActiveMode.BASELINE,
    )
    return PassAOutput(
        draft_answer="draft",
        updated_state=updated_state,
        self_model=SelfModel(
            stability_band=Band.HIGH,
            disruption_level=Band.LOW,
            mode_recommendation=ActiveMode.BASELINE,
            safe_depth=Band.MEDIUM,
            state_summary="stable",
        ),
        policy_profile=PolicyProfile(),
        memory_updates=[],
    )


def test_reading_position_persists_and_influences_next_turn_context(tmp_path):
    session_store = SessionStore(str(tmp_path / "sessions"))
    memory_store = MemoryStore(str(tmp_path / "memory"))
    session_store.start_session("s1", objective="rc2-r1")

    case = _load_case("protective_boundary")
    result = run_boundary_awareness_pass(
        user_intent=case["user_intent"],
        requested_capability=case["requested_capability"],
        execution_gate=ExecutionGateResult(**case["execution_gate"]),
    )

    prior_state = session_store.load_state()
    analyze_post_turn(
        pass_a_output=_build_pass_a_output(turn_id=1, session_id="s1", drift=0.08),
        prior_state=prior_state,
        session_store=session_store,
        memory_store=memory_store,
        boundary_awareness_result=result,
    )

    persisted = session_store.load_reading_position()
    assert persisted.preferred_zoom == "mechanism"

    # Next turn bridge consumes persisted reading_position.
    next_turn_context = boundary_residue_to_policy_context(
        stored_residue=session_store.load_boundary_residue(),
        current_state=session_store.load_state(),
        reading_position=persisted,
    )
    assert next_turn_context.prefer_style == "mechanism_first"
    assert next_turn_context.explanation_mode == "explicit"


def test_reading_position_recovers_after_mild_drift_on_following_turn(tmp_path):
    session_store = SessionStore(str(tmp_path / "sessions"))
    memory_store = MemoryStore(str(tmp_path / "memory"))
    session_store.start_session("s1", objective="rc2-r1")

    # Turn 1: boundary-aware shift to mechanism stance.
    case = _load_case("protective_boundary")
    result = run_boundary_awareness_pass(
        user_intent=case["user_intent"],
        requested_capability=case["requested_capability"],
        execution_gate=ExecutionGateResult(**case["execution_gate"]),
    )
    analyze_post_turn(
        pass_a_output=_build_pass_a_output(turn_id=1, session_id="s1", drift=0.08),
        prior_state=session_store.load_state(),
        session_store=session_store,
        memory_store=memory_store,
        boundary_awareness_result=result,
    )

    # Turn 2: no new boundary event, mild drift -> recover toward stable practical mode.
    analyze_post_turn(
        pass_a_output=_build_pass_a_output(turn_id=2, session_id="s1", drift=0.2),
        prior_state=session_store.load_state(),
        session_store=session_store,
        memory_store=memory_store,
        boundary_awareness_result=None,
    )

    recovered = session_store.load_reading_position()
    assert recovered.preferred_zoom == "practical"
    assert recovered.ambiguity_tolerance == Band.MEDIUM
