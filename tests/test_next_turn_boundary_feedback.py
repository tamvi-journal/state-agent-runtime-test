"""Phase 6 integration tests: prior boundary residue influences next-turn policy."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.boundary_awareness_engine import run_boundary_awareness_pass
from app.boundary_context_bridge import boundary_residue_to_policy_context
from app.memory_store import MemoryStore
from app.post_turn_analyzer import analyze_post_turn
from app.policy_gate import policy_gate
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
            stability_band=Band.HIGH,
            disruption_level=Band.LOW,
            mode_recommendation=ActiveMode.BASELINE,
            safe_depth=Band.MEDIUM,
            state_summary="stable",
        ),
        policy_profile=PolicyProfile(),
        memory_updates=[],
    )


def test_prior_protective_boundary_changes_next_turn_policy_context(tmp_path):
    session_store = SessionStore(str(tmp_path / "sessions"))
    memory_store = MemoryStore(str(tmp_path / "memory"))
    session_store.start_session("s1", objective="phase6")

    case = _load_case("protective_boundary")
    result = run_boundary_awareness_pass(
        user_intent=case["user_intent"],
        requested_capability=case["requested_capability"],
        execution_gate=ExecutionGateResult(**case["execution_gate"]),
    )

    prior_state = session_store.load_state()
    analyze_post_turn(
        pass_a_output=_build_pass_a_output(turn_id=1, session_id="s1"),
        prior_state=prior_state,
        session_store=session_store,
        memory_store=memory_store,
        boundary_awareness_result=result,
    )

    # Next turn reads latest residue into bounded policy context.
    next_turn_context = boundary_residue_to_policy_context(
        session_store.load_boundary_residue()
    )
    assert next_turn_context.has_boundary_residue is True
    assert next_turn_context.force_anchor_to_objective is True
    assert next_turn_context.prefer_style == "mechanism_first"

    self_model = SelfModel(
        stability_band=Band.HIGH,
        disruption_level=Band.LOW,
        mode_recommendation=ActiveMode.BASELINE,
        safe_depth=Band.HIGH,
        state_summary="stable",
    )

    baseline_policy = policy_gate(self_model=self_model, prior_deltas=[])
    feedback_policy = policy_gate(
        self_model=self_model,
        prior_deltas=[],
        boundary_context=next_turn_context,
    )

    assert baseline_policy.style == "default"
    assert baseline_policy.anchor_to_objective is False

    assert feedback_policy.style == "mechanism_first"
    assert feedback_policy.anchor_to_objective is True
