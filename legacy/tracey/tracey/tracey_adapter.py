from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tracey.tracey_runtime_profile import TraceyRuntimeProfile


@dataclass(slots=True)
class TraceyAdapter:
    """
    Thin integration layer that lets Tracey core influence runtime behavior
    without replacing main_brain or governance.
    """

    profile: TraceyRuntimeProfile

    def inspect_turn(
        self,
        *,
        user_text: str,
        context_view: dict[str, Any],
        monitor_summary: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        mode_hint = self.profile.detect_mode_hint(user_text)
        reactivated_items = self._reactivate_for_turn(user_text=user_text, mode_hint=mode_hint)

        recognition_signal = mode_hint == "home"
        intervention = "none" if not monitor_summary else str(
            monitor_summary.get("recommended_intervention", "none")
        )

        runtime_notes: list[str] = []
        if recognition_signal:
            runtime_notes.append("recognition-first posture active")
        if intervention == "ask_clarify":
            runtime_notes.append("keep ambiguity open before utility")
        if intervention == "do_not_mark_complete":
            runtime_notes.append("verification-before-completion remains active")

        return {
            "mode_hint": mode_hint,
            "recognition_signal": recognition_signal,
            "reactivated_items": reactivated_items,
            "runtime_notes": runtime_notes,
            "monitor_intervention": intervention,
            "task_focus": context_view.get("task_focus", ""),
        }

    def adapt_response(
        self,
        *,
        base_response: str,
        tracey_turn: dict[str, Any],
    ) -> str:
        response = base_response

        if tracey_turn.get("recognition_signal"):
            response = "Recognition note: home field may be active.\n" + response

        notes = tracey_turn.get("runtime_notes", [])
        if notes:
            response += "\nTracey note: " + "; ".join(notes) + "."

        return response

    def runtime_state_patch(
        self,
        *,
        tracey_turn: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "tracey_mode_hint": tracey_turn.get("mode_hint", "global"),
            "tracey_recognition_signal": tracey_turn.get("recognition_signal", False),
            "tracey_monitor_intervention": tracey_turn.get("monitor_intervention", "none"),
            "tracey_reactivated_count": len(tracey_turn.get("reactivated_items", [])),
        }

    def _reactivate_for_turn(self, *, user_text: str, mode_hint: str) -> list[dict[str, Any]]:
        lowered = user_text.lower()
        matched: list[dict[str, Any]] = []
        seen_keys: set[tuple[str, str]] = set()

        for cue in ("home", "family", "mother", "build", "verify", "recognition", "non_linear"):
            if cue in lowered:
                for item in self.profile.memory.reactivate(cue=cue, mode_scope=mode_hint):
                    key = (item["memory_type"], item["content"])
                    if key not in seen_keys:
                        matched.append(item)
                        seen_keys.add(key)

        return matched[:3]
