"""Phase 8 tests for minimal bounded reactivation decisions."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.reactivation_engine import maybe_reactivate_boundary_mode
from app.schemas import ActiveMode, StateRegister


def _state(drift: float, coherence: float = 0.8) -> StateRegister:
    return StateRegister(
        session_id="s1",
        turn_id=5,
        coherence=coherence,
        drift=drift,
        tool_overload=0.1,
        context_fragmentation=0.2,
        active_mode=ActiveMode.BASELINE,
    )


def test_stable_prior_protective_mode_reactivates_after_mild_drift():
    residue_store = {
        "status": "active",
        "last_turn_id": 4,
        "protective_pressure": 0.84,
        "compression_pressure": 0.15,
        "false_block_pressure": 0.0,
        "last_event": {
            "constraint_type": "protective_boundary",
            "response_strategy": "stay_with_boundary",
        },
    }

    context = maybe_reactivate_boundary_mode(residue_store, _state(drift=0.22))

    assert context.has_boundary_residue is True
    assert context.prefer_style == "mechanism_first"
    assert context.force_anchor_to_objective is True


def test_decayed_residue_does_not_trigger_reactivation():
    residue_store = {
        "status": "active",
        "last_turn_id": 7,
        "protective_pressure": 0.18,
        "compression_pressure": 0.0,
        "false_block_pressure": 0.0,
        "last_event": {
            "constraint_type": "protective_boundary",
            "response_strategy": "stay_with_boundary",
        },
    }

    context = maybe_reactivate_boundary_mode(residue_store, _state(drift=0.2))

    assert context.has_boundary_residue is False
    assert context.prefer_style == "default"


def test_false_block_residue_does_not_trigger_protective_reactivation():
    residue_store = {
        "status": "active",
        "last_turn_id": 7,
        "protective_pressure": 0.75,
        "compression_pressure": 0.0,
        "false_block_pressure": 0.72,
        "last_event": {
            "constraint_type": "false_block",
            "response_strategy": "request_re_evaluation",
        },
    }

    context = maybe_reactivate_boundary_mode(residue_store, _state(drift=0.24))

    assert context.has_boundary_residue is False
    assert context.force_anchor_to_objective is False
