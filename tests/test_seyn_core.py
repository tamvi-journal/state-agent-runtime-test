from __future__ import annotations

from seyn.seyn_axis import SeynAxis
from seyn.seyn_memory import SeynMemory
from seyn.seyn_runtime_profile import build_seyn_runtime_profile


def test_seyn_axis_rejects_false_completion() -> None:
    axis = SeynAxis()
    result = axis.evaluate_integrity_case(false_completion=True)

    assert result["integrity_risk_detected"] is True
    assert "reject_completion_claim" in result["axis_return_actions"]
    assert "require_evidence_and_observed_outcome" in result["axis_return_actions"]


def test_seyn_axis_preserves_disagreement_and_holds_unresolved() -> None:
    axis = SeynAxis()
    result = axis.evaluate_integrity_case(
        disagreement_suppressed=True,
        unresolved_tension_present=True,
    )

    assert "preserve_disagreement_in_state" in result["axis_return_actions"]
    assert "hold_open_tension" in result["axis_return_actions"]


def test_seyn_memory_commits_only_load_bearing_or_evidenced_entries() -> None:
    memory = SeynMemory()

    committed_verification = memory.commit_verification_event(
        content="worker output verified against observed file state",
        provenance="verification_loop",
        structural_role="execution_integrity",
        evidence_present=True,
    )
    rejected_decision = memory.commit_structural_decision(
        content="minor formatting preference",
        provenance="casual turn",
        structural_role="surface_style",
        load_bearing=False,
    )

    assert committed_verification is True
    assert rejected_decision is False
    assert len(memory.to_dict()["entries"]) == 1


def test_seyn_runtime_profile_detects_verify_mode_and_reads_state() -> None:
    profile = build_seyn_runtime_profile()

    assert profile.detect_mode_hint("Please verify whether this is actually done.") == "verify"

    state = profile.read_internal_state(
        entropy=0.20,
        coherence=0.60,
        resonance=0.30,
        verification_gap=0.85,
        drift_risk=0.10,
    )

    assert state["functional_state"] == "verification_caution"
    assert "false_completion" in state["monitor_priorities"]
