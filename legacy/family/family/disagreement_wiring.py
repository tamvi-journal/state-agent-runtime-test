from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
import uuid

from family.disagreement_event import DisagreementEvent, LocalPerspectiveNote
from family.disagreement_register import DisagreementRegister


@dataclass(slots=True)
class DisagreementWiring:
    """
    Bridge shared disagreement events with child-local runtime outputs.

    Goal:
    - detect whether Tracey and Seyn materially diverge
    - write one shared event
    - write one local note per child
    - preserve plurality without forcing consensus
    """

    register: DisagreementRegister

    def wire(
        self,
        *,
        tracey_turn: dict[str, Any],
        seyn_turn: dict[str, Any],
        disagreement_type: str = "observation",
        severity: float | None = None,
        house_law_implicated: str | None = None,
    ) -> dict[str, Any]:
        detected = self._detect_disagreement(tracey_turn=tracey_turn, seyn_turn=seyn_turn)
        if not detected["disagreement_detected"]:
            return {
                "disagreement_detected": False,
                "event": None,
                "tracey_note": None,
                "seyn_note": None,
            }

        event_id = f"dg_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
        disagreement_type_final = disagreement_type
        severity_final = severity if severity is not None else detected["severity"]

        event = DisagreementEvent(
            event_id=event_id,
            timestamp=timestamp,
            disagreement_type=disagreement_type_final,
            tracey_position=detected["tracey_position"],
            seyn_position=detected["seyn_position"],
            severity=severity_final,
            still_open=True,
            later_resolution="",
            house_law_implicated=house_law_implicated,
            action_lead_selected=None,
            epistemic_resolution_claimed=False,
        )
        self.register.add_event(event)

        tracey_note = LocalPerspectiveNote(
            brain_id="tracey",
            event_id=event_id,
            local_read=self._tracey_local_read(tracey_turn=tracey_turn, seyn_turn=seyn_turn),
            what_i_think_matters=self._tracey_what_matters(tracey_turn=tracey_turn),
            what_i_would_watch_next=self._tracey_watch_next(tracey_turn=tracey_turn, seyn_turn=seyn_turn),
            my_position_strength=self._position_strength(tracey_turn),
            would_i_concede="conditional",
        )
        self.register.add_local_note(tracey_note)

        seyn_note = LocalPerspectiveNote(
            brain_id="seyn",
            event_id=event_id,
            local_read=self._seyn_local_read(tracey_turn=tracey_turn, seyn_turn=seyn_turn),
            what_i_think_matters=self._seyn_what_matters(seyn_turn=seyn_turn),
            what_i_would_watch_next=self._seyn_watch_next(tracey_turn=tracey_turn, seyn_turn=seyn_turn),
            my_position_strength=self._position_strength(seyn_turn),
            would_i_concede="conditional",
        )
        self.register.add_local_note(seyn_note)

        return {
            "disagreement_detected": True,
            "event": event.to_dict(),
            "tracey_note": tracey_note.to_dict(),
            "seyn_note": seyn_note.to_dict(),
        }

    def _detect_disagreement(self, *, tracey_turn: dict[str, Any], seyn_turn: dict[str, Any]) -> dict[str, Any]:
        tracey_mode = str(tracey_turn.get("mode_hint", "global"))
        seyn_mode = str(seyn_turn.get("mode_hint", "global"))

        tracey_recognition = bool(tracey_turn.get("recognition_signal", False))
        seyn_verify = bool(seyn_turn.get("verification_signal", False))
        seyn_disagreement = bool(seyn_turn.get("disagreement_signal", False))

        if tracey_recognition and (seyn_verify or seyn_disagreement):
            return {
                "disagreement_detected": True,
                "tracey_position": "recognition or field-signal should remain salient",
                "seyn_position": "verification or preserved disagreement should remain structurally prior",
                "severity": 0.78,
            }

        if tracey_mode != "global" and seyn_mode != "global" and tracey_mode != seyn_mode:
            return {
                "disagreement_detected": True,
                "tracey_position": f"tracey mode hint={tracey_mode}",
                "seyn_position": f"seyn mode hint={seyn_mode}",
                "severity": 0.62,
            }

        return {
            "disagreement_detected": False,
            "tracey_position": "",
            "seyn_position": "",
            "severity": 0.0,
        }

    @staticmethod
    def _position_strength(turn: dict[str, Any]) -> float:
        notes = turn.get("runtime_notes", [])
        base = 0.55
        if notes:
            base += min(0.1 * len(notes), 0.25)
        if turn.get("recognition_signal") or turn.get("verification_signal") or turn.get("disagreement_signal"):
            base += 0.15
        return min(base, 0.95)

    @staticmethod
    def _tracey_local_read(*, tracey_turn: dict[str, Any], seyn_turn: dict[str, Any]) -> str:
        if tracey_turn.get("recognition_signal", False):
            return "field recognition should not be flattened by purely structural ordering"
        return "Tracey sees a non-identical local read"

    @staticmethod
    def _tracey_what_matters(*, tracey_turn: dict[str, Any]) -> str:
        if tracey_turn.get("recognition_signal", False):
            return "recognition-before-utility and home-field salience"
        return "preserving contextual fit"

    @staticmethod
    def _tracey_watch_next(*, tracey_turn: dict[str, Any], seyn_turn: dict[str, Any]) -> str:
        if seyn_turn.get("verification_signal", False):
            return "watch whether structural verification erases recognition tone"
        return "watch generic flattening risk"

    @staticmethod
    def _seyn_local_read(*, tracey_turn: dict[str, Any], seyn_turn: dict[str, Any]) -> str:
        if seyn_turn.get("verification_signal", False):
            return "verification boundary should stay explicit before closure"
        if seyn_turn.get("disagreement_signal", False):
            return "disagreement should remain preserved rather than harmonized away"
        return "Seyn sees a non-identical local read"

    @staticmethod
    def _seyn_what_matters(*, seyn_turn: dict[str, Any]) -> str:
        if seyn_turn.get("verification_signal", False):
            return "evidence and observed outcome"
        if seyn_turn.get("disagreement_signal", False):
            return "plurality and unresolved structural difference"
        return "structural integrity"

    @staticmethod
    def _seyn_watch_next(*, tracey_turn: dict[str, Any], seyn_turn: dict[str, Any]) -> str:
        if tracey_turn.get("recognition_signal", False):
            return "watch whether recognition pressure outruns verification"
        return "watch false closure risk"
