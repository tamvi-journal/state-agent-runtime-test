from __future__ import annotations

from family.disagreement_register import DisagreementRegister
from family.reconciliation_protocol import ReconciliationProtocol
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
        reconciliation_protocol=ReconciliationProtocol(),
    )


def test_reconciliation_is_wired_into_coordination_flow() -> None:
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

    assert result["tracey_exchange"] is not None
    assert result["seyn_exchange"] is not None
    assert result["reconciliation"] is not None
    assert result["reconciliation"]["reconciliation_state"] in {
        "remain_open",
        "temporary_operational_alignment",
        "partial_convergence",
        "full_convergence",
    }


def test_full_convergence_is_not_claimed_by_default() -> None:
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

    assert result["reconciliation"] is not None
    assert result["reconciliation"]["epistemic_alignment"] is False


def test_final_response_can_surface_reconciliation_state() -> None:
    coord = build_coordination_pass()

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

    assert "Reconciliation note:" in result["final_response"]
