from __future__ import annotations

from laws.authority_law import AuthorityLaw
from laws.verification_vs_monitor_law import VerificationVsMonitorLaw
from laws.family_boundary_law import FamilyBoundaryLaw
from laws.memory_commit_law import MemoryCommitLaw
from laws.anti_fabrication_law import AntiFabricationLaw
from laws.ambiguity_halt_law import AmbiguityHaltLaw
from memory_runtime.continuity_gateway import ContinuityGateway


def test_authority_law_keeps_main_brain_as_authority() -> None:
    law = AuthorityLaw()

    main = law.evaluate(actor="main_brain", requested_action="synthesize")
    worker = law.evaluate(actor="worker", requested_action="synthesize")

    assert main.allowed is True
    assert worker.allowed is False
    assert worker.authority_holder == "main_brain"


def test_verification_and_monitor_roles_do_not_collapse() -> None:
    law = VerificationVsMonitorLaw()
    boundaries = law.boundaries()

    assert boundaries["verification"]["may_assert_grounding"] is True
    assert boundaries["verification"]["may_block_progress"] is False
    assert boundaries["monitor"]["may_block_progress"] is True
    assert boundaries["monitor"]["may_assert_grounding"] is False


def test_family_signal_does_not_bypass_verification_or_refusal() -> None:
    law = FamilyBoundaryLaw()
    decision = law.evaluate(family_signal_detected=True)

    assert decision.recognition_priority_boost is True
    assert decision.increases_epistemic_certainty is False
    assert decision.bypasses_verification is False
    assert decision.bypasses_refusal is False


def test_memory_commit_requires_structural_conditions() -> None:
    law = MemoryCommitLaw()

    allowed = law.evaluate(
        object_type="disagreement_event",
        unresolved=True,
    )
    denied = law.evaluate(
        object_type="worker_payload",
        verified=False,
    )

    assert allowed.commit_allowed is True
    assert denied.commit_allowed is False


def test_anti_fabrication_holds_when_evidence_is_weak() -> None:
    law = AntiFabricationLaw()
    decision = law.evaluate(
        evidence_strength=0.30,
        fabrication_pressure=False,
        hypothesis_possible=True,
    )

    assert decision.strong_claim_allowed is False
    assert decision.should_hold_open is True
    assert decision.should_switch_to_hypothesis is True


def test_ambiguity_halt_triggers_on_action_required_turn() -> None:
    law = AmbiguityHaltLaw()
    decision = law.evaluate(
        ambiguity_score=0.85,
        task_type="execution",
        action_required=True,
    )

    assert decision.should_halt is True
    assert decision.should_clarify is True


def test_continuity_gateway_separates_read_and_write_rules() -> None:
    gateway = ContinuityGateway()

    read = gateway.read_access(
        task_type="architecture",
        active_mode="build",
        archive_needed=True,
        family_signal_detected=False,
    )
    write = gateway.write_access(
        object_type="tracey_memory_item",
        load_bearing=True,
        verified=False,
        unresolved=False,
    )

    assert read["may_read_live_state"] is True
    assert read["may_read_archive"] is True
    assert write["commit_allowed"] is True
    assert write["should_write_live_state"] is True
