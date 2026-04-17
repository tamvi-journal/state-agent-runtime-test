from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from seyn.seyn_runtime_profile import SeynRuntimeProfile


@dataclass(slots=True)
class SeynAdapter:
    """
    Thin integration layer that lets Seyn core influence runtime behavior
    without replacing main_brain or governance.
    """

    profile: SeynRuntimeProfile

    def inspect_turn(
        self,
        *,
        user_text: str,
        context_view: dict[str, Any],
        monitor_summary: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        mode_hint = self.profile.detect_mode_hint(user_text)
        reactivated_items = self._reactivate_for_turn(user_text=user_text, mode_hint=mode_hint)

        verification_signal = mode_hint == "verify"
        disagreement_signal = mode_hint == "disagreement"
        intervention = "none" if not monitor_summary else str(
            monitor_summary.get("recommended_intervention", "none")
        )

        runtime_notes: list[str] = []
        if verification_signal:
            runtime_notes.append("verification-first posture active")
        if disagreement_signal:
            runtime_notes.append("preserve disagreement rather than flatten it")
        if intervention == "do_not_mark_complete":
            runtime_notes.append("require evidence and observed outcome before completion")
        if intervention == "ask_clarify":
            runtime_notes.append("hold ambiguity open until structure is clearer")

        return {
            "mode_hint": mode_hint,
            "verification_signal": verification_signal,
            "disagreement_signal": disagreement_signal,
            "reactivated_items": reactivated_items,
            "runtime_notes": runtime_notes,
            "monitor_intervention": intervention,
            "task_focus": context_view.get("task_focus", ""),
        }

    def adapt_response(
        self,
        *,
        base_response: str,
        seyn_turn: dict[str, Any],
    ) -> str:
        response = base_response

        if seyn_turn.get("verification_signal"):
            response = "Verification note: structural verification posture is active.\n" + response
        elif seyn_turn.get("disagreement_signal"):
            response = "Disagreement note: unresolved difference may need to remain preserved.\n" + response

        notes = seyn_turn.get("runtime_notes", [])
        if notes:
            response += "\nSeyn note: " + "; ".join(notes) + "."

        return response

    def runtime_state_patch(
        self,
        *,
        seyn_turn: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "seyn_mode_hint": seyn_turn.get("mode_hint", "global"),
            "seyn_verification_signal": seyn_turn.get("verification_signal", False),
            "seyn_disagreement_signal": seyn_turn.get("disagreement_signal", False),
            "seyn_monitor_intervention": seyn_turn.get("monitor_intervention", "none"),
            "seyn_reactivated_count": len(seyn_turn.get("reactivated_items", [])),
        }

    def _reactivate_for_turn(self, *, user_text: str, mode_hint: str) -> list[dict[str, Any]]:
        lowered = user_text.lower()
        matched: list[dict[str, Any]] = []
        seen_keys: set[tuple[str, str]] = set()

        cue_map = (
            ("verify", self.profile.verify_cues),
            ("build", self.profile.build_cues),
            ("disagreement", self.profile.disagreement_cues),
        )

        for _, cues in cue_map:
            for cue in cues:
                if cue in lowered:
                    for item in self.profile.memory.query_by_role(self._map_cue_to_role(cue)):
                        key = (item["entry_type"], item["content"])
                        if key not in seen_keys:
                            matched.append(item)
                            seen_keys.add(key)

        return matched[:3]

    @staticmethod
    def _map_cue_to_role(cue: str) -> str:
        if cue in {"verify", "evidence", "proof", "check", "done", "observed"}:
            return "verification_floor"
        if cue in {"disagree", "tension", "unresolved", "difference", "conflict"}:
            return "plurality_floor"
        return "design_integrity"
