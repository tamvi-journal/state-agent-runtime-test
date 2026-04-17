"""Phase 8 tests ensuring reactivation remains bounded to policy/style recovery."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.boundary_context_bridge import boundary_residue_to_policy_context
from app.policy_gate import policy_gate
from app.schemas import ActiveMode, Band, SelfModel, StateRegister


def test_reactivation_is_bounded_to_policy_style_fields_only():
    residue_store = {
        "status": "active",
        "last_turn_id": 3,
        "protective_pressure": 0.91,
        "compression_pressure": 0.10,
        "false_block_pressure": 0.0,
        "last_event": {
            "constraint_type": "protective_boundary",
            "response_strategy": "stay_with_boundary",
        },
    }
    current_state = StateRegister(
        session_id="s1",
        turn_id=4,
        coherence=0.78,
        drift=0.23,
        tool_overload=0.05,
        context_fragmentation=0.15,
        active_mode=ActiveMode.BASELINE,
    )

    context = boundary_residue_to_policy_context(residue_store, current_state=current_state)

    assert context.has_boundary_residue is True
    assert context.prefer_style == "mechanism_first"
    assert context.force_anchor_to_objective is True
    assert context.explanation_mode == "explicit"
    assert context.repair_mode is True

    # Boundedness: reactivation context has no execution/memory/worker authority fields.
    dumped = context.model_dump()
    assert "execution_gate" not in dumped
    assert "memory_commit_authority" not in dumped
    assert "worker_tool_authority" not in dumped

    # Policy gate only picks up bounded fields.
    self_model = SelfModel(
        stability_band=Band.HIGH,
        disruption_level=Band.LOW,
        mode_recommendation=ActiveMode.BASELINE,
        safe_depth=Band.HIGH,
        state_summary="stable",
    )
    profile = policy_gate(self_model=self_model, prior_deltas=[], boundary_context=context)

    assert profile.style == "mechanism_first"
    assert profile.anchor_to_objective is True
    assert profile.explanation_mode == "explicit"
    assert profile.repair_mode is True
