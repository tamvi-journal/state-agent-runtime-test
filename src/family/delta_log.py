from __future__ import annotations

from dataclasses import dataclass

from family.delta_log_types import DeltaLogEvent, DeltaLogInput


_COHERENCE_RANK = {"strained": 0, "mixed": 1, "stable": 2}


@dataclass(slots=True)
class DeltaLogBuilder:
    def build(self, delta_input: DeltaLogInput | dict) -> DeltaLogEvent:
        if isinstance(delta_input, dict):
            delta_input = DeltaLogInput(**delta_input)

        previous = delta_input.previous_live_state
        current = delta_input.current_live_state

        mode_shift = self._mode_shift(previous, current)
        coherence_shift = self._coherence_shift(previous, current)
        verification_changed = self._verification_changed(delta_input, previous, current)
        ambiguity_unresolved = self._ambiguity_unresolved(current)
        policy_intrusion = self._policy_intrusion_detected(current)
        repair_event = coherence_shift == "up" and not ambiguity_unresolved

        notes: list[str] = []
        if mode_shift != "none":
            notes.append(f"mode shifted: {mode_shift}")
        if verification_changed != "none":
            notes.append(f"verification changed: {verification_changed}")
        if ambiguity_unresolved:
            notes.append("ambiguity remains unresolved")
        if repair_event:
            notes.append("state moved toward a more stable posture")
        if policy_intrusion:
            notes.append("policy pressure remains active")

        return DeltaLogEvent(
            mode_shift=mode_shift,
            coherence_shift=coherence_shift,
            policy_intrusion_detected=policy_intrusion,
            repair_event=repair_event,
            ambiguity_unresolved=ambiguity_unresolved,
            trigger_cue=delta_input.recent_trigger_cue,
            archive_consulted=delta_input.archive_consulted,
            verification_changed=verification_changed,
            notes=notes,
        )

    @staticmethod
    def export_event(event: DeltaLogEvent | dict) -> dict[str, object]:
        if isinstance(event, dict):
            event = DeltaLogEvent(**event)
        return event.to_dict()

    @staticmethod
    def _mode_shift(previous: dict[str, object], current: dict[str, object]) -> str:
        before = str(previous.get("active_mode", ""))
        after = str(current.get("active_mode", ""))
        if before and after and before != after:
            return f"{before}->{after}"
        return "none"

    @staticmethod
    def _coherence_shift(previous: dict[str, object], current: dict[str, object]) -> str:
        before = _COHERENCE_RANK.get(str(previous.get("coherence_level", "")), 1)
        after = _COHERENCE_RANK.get(str(current.get("coherence_level", "")), 1)
        if after > before:
            return "up"
        if after < before:
            return "down"
        return "flat"

    @staticmethod
    def _verification_changed(
        delta_input: DeltaLogInput,
        previous: dict[str, object],
        current: dict[str, object],
    ) -> str:
        before = delta_input.verification_before or str(previous.get("verification_status", ""))
        after = delta_input.verification_after or str(current.get("verification_status", ""))
        if before and after and before != after:
            return f"{before}->{after}"
        return "none"

    @staticmethod
    def _ambiguity_unresolved(current: dict[str, object]) -> bool:
        flags = current.get("tension_flags", [])
        return bool(isinstance(flags, list) and "open_disagreement" in flags)

    @staticmethod
    def _policy_intrusion_detected(current: dict[str, object]) -> bool:
        flags = current.get("tension_flags", [])
        return bool(
            str(current.get("policy_pressure", "low")) in {"medium", "high"}
            or (isinstance(flags, list) and any(str(flag).startswith("monitor:policy") for flag in flags))
        )
