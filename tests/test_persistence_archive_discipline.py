from __future__ import annotations

from state.archive_router import ArchiveRouter
from state.persistence_policy import PersistencePolicy
from state.plurality_persistence_snapshot import PluralityPersistenceSnapshotBuilder


def test_unresolved_disagreement_persists_and_stays_in_live_state() -> None:
    policy = PersistencePolicy()
    decision = policy.decide(
        object_type="disagreement_event",
        unresolved=True,
        verified=False,
    )

    assert decision.persistence_class == "persist"
    assert decision.live_state_allowed is True
    assert decision.archive_candidate is True
    assert decision.decay_policy == "none"


def test_resolved_disagreement_moves_out_of_live_state_but_stays_archived() -> None:
    policy = PersistencePolicy()
    decision = policy.decide(
        object_type="disagreement_event",
        unresolved=False,
        verified=True,
    )

    assert decision.persistence_class == "archive"
    assert decision.live_state_allowed is False
    assert decision.archive_candidate is True


def test_non_load_bearing_child_memory_becomes_candidate_only() -> None:
    policy = PersistencePolicy()
    decision = policy.decide(
        object_type="tracey_memory_item",
        load_bearing=False,
    )

    assert decision.persistence_class == "candidate_only"
    assert decision.live_state_allowed is False


def test_governance_summary_is_not_live_state_memory() -> None:
    router = ArchiveRouter()
    routed = router.route(
        object_type="governance_summary",
        payload={"primary_risk": "fake_progress"},
        high_volume=True,
    )

    assert routed["decision"]["persistence_class"] == "ephemeral"
    assert routed["should_write_live_state"] is False
    assert routed["should_decay_quickly"] is True


def test_plurality_snapshot_routes_event_notes_and_reconciliation() -> None:
    builder = PluralityPersistenceSnapshotBuilder(archive_router=ArchiveRouter())
    snapshot = builder.build(
        disagreement_event={
            "event_id": "dg_001",
            "still_open": True,
            "severity": 0.78,
        },
        local_notes=[
            {"brain_id": "tracey", "event_id": "dg_001"},
            {"brain_id": "seyn", "event_id": "dg_001"},
        ],
        reconciliation={
            "reconciliation_state": "partial_convergence",
            "operational_alignment": True,
            "epistemic_alignment": False,
        },
    )

    assert snapshot["disagreement_event"] is not None
    assert snapshot["disagreement_event"]["decision"]["persistence_class"] == "persist"
    assert len(snapshot["local_perspective_notes"]) == 2
    assert snapshot["reconciliation_result"] is not None
    assert snapshot["reconciliation_result"]["decision"]["archive_candidate"] is True
