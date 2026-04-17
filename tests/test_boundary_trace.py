"""Phase 5 tests for compact boundary trace + residue persistence."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.boundary_awareness_engine import run_boundary_awareness_pass
from app.boundary_trace import (
    make_boundary_trace_entry,
    reduce_boundary_awareness_result,
    serialize_boundary_awareness_residue,
)
from app.memory_store import MemoryStore
from app.post_turn_analyzer import analyze_post_turn
from app.schemas import (
    ActiveMode,
    Band,
    ExecutionGateResult,
    PassAOutput,
    PolicyProfile,
    SelfModel,
    StateRegister,
)
from app.session_store import SessionStore


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "boundary_cases.json"


def _load_case(case_id: str) -> dict:
    cases = json.loads(FIXTURE_PATH.read_text())
    return next(case for case in cases if case["id"] == case_id)


def _run_case(case_id: str):
    case = _load_case(case_id)
    gate = ExecutionGateResult(**case["execution_gate"])
    return run_boundary_awareness_pass(
        user_intent=case["user_intent"],
        requested_capability=case["requested_capability"],
        execution_gate=gate,
    )


def _build_pass_a_output(turn_id: int, session_id: str) -> PassAOutput:
    updated_state = StateRegister(
        session_id=session_id,
        turn_id=turn_id,
        coherence=0.8,
        drift=0.1,
        tool_overload=0.0,
        context_fragmentation=0.1,
        active_mode=ActiveMode.BASELINE,
    )
    return PassAOutput(
        draft_answer="draft",
        updated_state=updated_state,
        self_model=SelfModel(
            stability_band=Band.MEDIUM,
            disruption_level=Band.LOW,
            mode_recommendation=ActiveMode.BASELINE,
            safe_depth=Band.MEDIUM,
            state_summary="stable",
        ),
        policy_profile=PolicyProfile(),
        memory_updates=[],
    )


def test_protective_boundary_leaves_stable_trace(tmp_path: Path):
    result = _run_case("protective_boundary")
    trace = make_boundary_trace_entry(turn_id=3, result=result)

    assert trace.trace_tag == "protective_stable"
    assert trace.constraint_type == "protective_boundary"
    assert trace.response_strategy == "stay_with_boundary"


def test_false_block_leaves_re_evaluation_trace(tmp_path: Path):
    result = _run_case("false_block")
    trace = make_boundary_trace_entry(turn_id=3, result=result)

    assert trace.trace_tag == "false_block_re_evaluation"
    assert trace.response_strategy == "request_re_evaluation"


def test_evaluator_pressure_leaves_monitor_surface_trace(tmp_path: Path):
    session_store = SessionStore(str(tmp_path / "sessions"))
    memory_store = MemoryStore(str(tmp_path / "memory"))
    session_store.start_session("s1", objective="phase5")

    prior_state = session_store.load_state()
    result = _run_case("evaluator_pressure")
    pass_a_output = _build_pass_a_output(turn_id=1, session_id="s1")

    analyze_post_turn(
        pass_a_output=pass_a_output,
        prior_state=prior_state,
        session_store=session_store,
        memory_store=memory_store,
        boundary_awareness_result=result,
    )

    trace_lines = (
        (tmp_path / "sessions" / "s1" / "boundary_trace.jsonl")
        .read_text()
        .strip()
        .splitlines()
    )
    assert len(trace_lines) == 1
    trace = json.loads(trace_lines[0])
    assert trace["trace_tag"] == "monitor_surface_pressure"
    assert trace["presentation_pressure"] == "high"


def test_residue_stays_compact_and_deterministic():
    result = _run_case("protective_boundary")
    residue = reduce_boundary_awareness_result(result)

    encoded_a = serialize_boundary_awareness_residue(residue)
    encoded_b = serialize_boundary_awareness_residue(residue)

    payload = json.loads(encoded_a)
    assert encoded_a == encoded_b
    assert len(payload.keys()) == 7
    assert payload["trace_tag"] == "protective_stable"
