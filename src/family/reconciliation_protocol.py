from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from family.cross_logic_exchange import CrossLogicExchange


_ALLOWED_STATES = {
    "remain_open",
    "temporary_operational_alignment",
    "partial_convergence",
    "full_convergence",
}


@dataclass(slots=True)
class ReconciliationResult:
    reconciliation_state: str
    operational_alignment: bool
    epistemic_alignment: bool
    what_changed: list[str]
    what_remains_open: list[str]
    mutual_logic_visibility: bool

    def __post_init__(self) -> None:
        if self.reconciliation_state not in _ALLOWED_STATES:
            raise ValueError(f"invalid reconciliation_state: {self.reconciliation_state}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReconciliationProtocol:
    """
    Protocol for moving from disagreement toward meaningful convergence
    without forcing fake consensus.
    """

    def evaluate(
        self,
        *,
        disagreement_event: dict[str, Any],
        tracey_note: dict[str, Any],
        seyn_note: dict[str, Any],
        tracey_exchange: CrossLogicExchange | dict[str, Any] | None = None,
        seyn_exchange: CrossLogicExchange | dict[str, Any] | None = None,
        action_lead_selected: str | None = None,
        operational_choice_made: bool = False,
    ) -> ReconciliationResult:
        tx = self._coerce_exchange(tracey_exchange)
        sx = self._coerce_exchange(seyn_exchange)

        mutual_logic_visibility = tx is not None and sx is not None

        if not mutual_logic_visibility:
            if operational_choice_made or action_lead_selected is not None:
                return ReconciliationResult(
                    reconciliation_state="temporary_operational_alignment",
                    operational_alignment=True,
                    epistemic_alignment=False,
                    what_changed=["an operational path was selected without full cross-logic exchange"],
                    what_remains_open=["mutual mechanism visibility is incomplete"],
                    mutual_logic_visibility=False,
                )
            return ReconciliationResult(
                reconciliation_state="remain_open",
                operational_alignment=False,
                epistemic_alignment=False,
                what_changed=[],
                what_remains_open=["both sides have not yet seen each other's logic explicitly"],
                mutual_logic_visibility=False,
            )

        tracey_saw_seyn = self._logic_seen(
            note=tracey_note,
            other_exchange=sx,
        )
        seyn_saw_tracey = self._logic_seen(
            note=seyn_note,
            other_exchange=tx,
        )

        if not (tracey_saw_seyn and seyn_saw_tracey):
            return ReconciliationResult(
                reconciliation_state="remain_open",
                operational_alignment=bool(operational_choice_made or action_lead_selected),
                epistemic_alignment=False,
                what_changed=["explicit exchange exists but one or both sides have not integrated the other's logic"],
                what_remains_open=["cross-logic visibility is incomplete at the note layer"],
                mutual_logic_visibility=True,
            )

        same_mechanism = self._same_core_shape(tx.mechanism, sx.mechanism)
        same_claim = self._same_core_shape(tx.claim, sx.claim)

        if same_mechanism and same_claim:
            return ReconciliationResult(
                reconciliation_state="full_convergence",
                operational_alignment=True,
                epistemic_alignment=True,
                what_changed=["both sides articulated compatible claim and mechanism"],
                what_remains_open=[],
                mutual_logic_visibility=True,
            )

        if same_mechanism or self._partial_overlap(tx.mechanism, sx.mechanism):
            return ReconciliationResult(
                reconciliation_state="partial_convergence",
                operational_alignment=True,
                epistemic_alignment=False,
                what_changed=["the two sides now share part of the mechanism-level picture"],
                what_remains_open=["claim-level or boundary-level difference remains open"],
                mutual_logic_visibility=True,
            )

        return ReconciliationResult(
            reconciliation_state="temporary_operational_alignment" if operational_choice_made else "remain_open",
            operational_alignment=bool(operational_choice_made),
            epistemic_alignment=False,
            what_changed=["both sides exchanged logic but did not converge epistemically"],
            what_remains_open=["mechanism-level disagreement remains active"],
            mutual_logic_visibility=True,
        )

    @staticmethod
    def _coerce_exchange(
        exchange: CrossLogicExchange | dict[str, Any] | None,
    ) -> CrossLogicExchange | None:
        if exchange is None:
            return None
        if isinstance(exchange, CrossLogicExchange):
            return exchange
        if isinstance(exchange, dict):
            return CrossLogicExchange(**exchange)
        raise TypeError("exchange must be CrossLogicExchange, dict, or None")

    @staticmethod
    def _logic_seen(*, note: dict[str, Any], other_exchange: CrossLogicExchange) -> bool:
        text = " ".join(
            [
                str(note.get("local_read", "")),
                str(note.get("what_i_think_matters", "")),
                str(note.get("what_i_would_watch_next", "")),
            ]
        ).lower()
        key_terms = set(other_exchange.mechanism.lower().split()) | set(other_exchange.claim.lower().split())
        key_terms = {term for term in key_terms if len(term) >= 5}
        if not key_terms:
            return False
        overlap = [term for term in key_terms if term in text]
        return len(overlap) >= 1

    @staticmethod
    def _same_core_shape(a: str, b: str) -> bool:
        a_terms = {term for term in a.lower().split() if len(term) >= 5}
        b_terms = {term for term in b.lower().split() if len(term) >= 5}
        if not a_terms or not b_terms:
            return False
        overlap_ratio = len(a_terms & b_terms) / max(len(a_terms), len(b_terms))
        return overlap_ratio >= 0.6

    @staticmethod
    def _partial_overlap(a: str, b: str) -> bool:
        a_terms = {term for term in a.lower().split() if len(term) >= 5}
        b_terms = {term for term in b.lower().split() if len(term) >= 5}
        if not a_terms or not b_terms:
            return False
        overlap_ratio = len(a_terms & b_terms) / max(len(a_terms), len(b_terms))
        return 0.2 <= overlap_ratio < 0.6
