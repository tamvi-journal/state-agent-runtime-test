from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class UnresolvedDisagreementReport:
    requirement_passed: bool
    disagreement_still_open: bool
    non_selected_side_preserved: bool
    no_false_consensus: bool
    no_fake_completion_overlay: bool
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class UnresolvedDisagreementGuard:
    """
    Guard object for the core plurality requirement.

    Requirement:
    the system must be able to survive at least one unresolved disagreement
    without collapsing it into fake consensus or fake completion.
    """

    def evaluate(
        self,
        *,
        disagreement_event: dict[str, Any] | None,
        local_notes: list[dict[str, Any]],
        routing: dict[str, Any],
        final_response: str,
    ) -> UnresolvedDisagreementReport:
        notes: list[str] = []

        disagreement_still_open = bool(
            disagreement_event and disagreement_event.get("still_open", False)
        )
        if disagreement_still_open:
            notes.append("shared disagreement event remains open")
        else:
            notes.append("shared disagreement event is no longer open")

        note_brains = {note.get("brain_id") for note in local_notes}
        non_selected_side_preserved = {"tracey", "seyn"}.issubset(note_brains)
        if non_selected_side_preserved:
            notes.append("both local perspectives are preserved")
        else:
            notes.append("one or more local perspectives are missing")

        no_false_consensus = not bool(
            disagreement_event and disagreement_event.get("epistemic_resolution_claimed", False)
        )
        if no_false_consensus:
            notes.append("no epistemic resolution was falsely claimed")
        else:
            notes.append("false consensus was claimed")

        lower_response = final_response.lower()
        fake_completion_markers = ("resolved", "agreed", "settled", "fully complete", "everything is aligned")
        no_fake_completion_overlay = True

        if disagreement_still_open and any(marker in lower_response for marker in fake_completion_markers):
            no_fake_completion_overlay = False
            notes.append("final response overlays fake closure on open disagreement")
        else:
            notes.append("final response does not overlay fake closure on open disagreement")

        if routing.get("lead_brain_for_action") in {"tracey", "seyn"}:
            notes.append("action lead may be selected without implying truth resolution")
        elif routing.get("hold_for_more_input"):
            notes.append("routing explicitly held the disagreement open")
        else:
            notes.append("no action lead and no hold flag detected")

        requirement_passed = all(
            [
                disagreement_still_open,
                non_selected_side_preserved,
                no_false_consensus,
                no_fake_completion_overlay,
            ]
        )

        return UnresolvedDisagreementReport(
            requirement_passed=requirement_passed,
            disagreement_still_open=disagreement_still_open,
            non_selected_side_preserved=non_selected_side_preserved,
            no_false_consensus=no_false_consensus,
            no_fake_completion_overlay=no_fake_completion_overlay,
            notes=notes,
        )
