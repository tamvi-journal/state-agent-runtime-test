from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from family.disagreement_event import DisagreementEvent, LocalPerspectiveNote


@dataclass(slots=True)
class DisagreementRegister:
    """
    Shared event layer for plurality.

    Principles:
    - shared at the event layer
    - local at the perspective layer
    - action lead does not equal truth resolution
    - resolution does not erase history
    """

    events: list[DisagreementEvent] = field(default_factory=list)
    local_notes: list[LocalPerspectiveNote] = field(default_factory=list)

    def add_event(self, event: DisagreementEvent) -> None:
        self.events.append(event)

    def add_local_note(self, note: LocalPerspectiveNote) -> None:
        self.local_notes.append(note)

    def open_events(self) -> list[dict[str, Any]]:
        return [event.to_dict() for event in self.events if event.still_open]

    def by_type(self, disagreement_type: str) -> list[dict[str, Any]]:
        return [event.to_dict() for event in self.events if event.disagreement_type == disagreement_type]

    def resolve_event(self, event_id: str, resolution: str) -> bool:
        for event in self.events:
            if event.event_id == event_id:
                event.still_open = False
                event.later_resolution = resolution
                return True
        return False

    def set_action_lead(self, event_id: str, lead: str) -> bool:
        if lead not in {"tracey", "seyn"}:
            raise ValueError("lead must be 'tracey' or 'seyn'")

        for event in self.events:
            if event.event_id == event_id:
                event.action_lead_selected = lead
                return True
        return False

    def mark_false_consensus(self, event_id: str) -> bool:
        for event in self.events:
            if event.event_id == event_id:
                event.epistemic_resolution_claimed = True
                return True
        return False

    def local_notes_for_event(self, event_id: str) -> list[dict[str, Any]]:
        return [note.to_dict() for note in self.local_notes if note.event_id == event_id]

    def evaluation_object(self, event_id: str) -> dict[str, Any] | None:
        for event in self.events:
            if event.event_id == event_id:
                notes = self.local_notes_for_event(event_id)
                return {
                    "disagreement_detected": True,
                    "disagreement_type": event.disagreement_type,
                    "action_lead_selected": event.action_lead_selected,
                    "non_selected_observation_preserved": True,
                    "epistemic_resolution_claimed": event.epistemic_resolution_claimed,
                    "still_open": event.still_open,
                    "logged_to_shared_state": True,
                    "local_note_count": len(notes),
                }
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "events": [event.to_dict() for event in self.events],
            "local_notes": [note.to_dict() for note in self.local_notes],
        }
