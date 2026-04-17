from __future__ import annotations

from family.house_laws import HouseLaws
from family.refusal_policy import RefusalPolicy
from family.runtime_security import RuntimeSecurityBoundaries
from family.shared_ontology import SharedOntology


def test_house_laws_detect_fake_completion() -> None:
    laws = HouseLaws()
    result = laws.evaluate(
        recognition_real=True,
        completion_verified=False,
        disagreement_preserved=True,
        silence_real=True,
    )

    assert result["violation_detected"] is True
    violated_names = {v["law_name"] for v in result["violations"]}
    assert "do_not_fake_completion" in violated_names


def test_refusal_policy_hold_open_on_verification_gap() -> None:
    policy = RefusalPolicy()
    decision = policy.evaluate(
        retrieval_success=True,
        verification_status="unknown",
        meaningful_disagreement_open=False,
        mode_confidence=0.90,
        stakes_signal=0.70,
        evidence_strength=0.90,
        fabrication_pressure=False,
        hypothesis_possible=True,
    )

    assert decision.refusal_type == "hold_open"
    assert decision.firm_claim_allowed is False


def test_runtime_security_unknown_object_goes_to_inspection() -> None:
    security = RuntimeSecurityBoundaries()
    decision = security.classify(object_type="repo", trust_stage="unknown")

    assert decision.recommended_zone == "inspection"
    assert decision.can_execute is False
    assert decision.requires_approval is True


def test_shared_ontology_labels_verification_caution() -> None:
    ontology = SharedOntology()
    label = ontology.label_state(
        entropy=0.20,
        coherence=0.60,
        resonance=0.40,
        verification_gap=0.85,
        drift_risk=0.10,
    )

    assert label == "verification_caution"
