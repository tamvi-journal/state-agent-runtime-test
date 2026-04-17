from __future__ import annotations

from dataclasses import dataclass

from family.live_state_types import LiveState, LiveStateInput


@dataclass(slots=True)
class LiveStateBuilder:
    def build(self, live_input: LiveStateInput | dict) -> LiveState:
        if isinstance(live_input, dict):
            live_input = LiveStateInput(**live_input)

        context_view = live_input.context_view
        mode_result = live_input.mode_inference_result
        verification_status = live_input.verification_status or str(context_view.get("verification_status", ""))

        active_mode = str(mode_result.get("active_mode", "")) or str(context_view.get("active_mode", "")) or "care"
        current_axis = self._derive_current_axis(live_input, context_view, active_mode)
        tension_flags = self._derive_tension_flags(live_input, context_view, verification_status)
        coherence_level = self._derive_coherence_level(
            tension_flags=tension_flags,
            disagreement_open=live_input.disagreement_open,
            confidence=float(mode_result.get("confidence", 0.0) or 0.0),
        )
        policy_pressure = self._derive_policy_pressure(live_input.monitor_summary)
        continuity_anchor = self._derive_continuity_anchor(live_input, context_view)
        user_signal = str(context_view.get("task_focus", "")) or continuity_anchor or active_mode
        archive_needed = self._derive_archive_needed(tension_flags, context_view)

        return LiveState(
            active_mode=active_mode,
            current_axis=current_axis,
            coherence_level=coherence_level,
            tension_flags=tension_flags,
            policy_pressure=policy_pressure,
            active_project=live_input.active_project or str(context_view.get("active_project", "")),
            continuity_anchor=continuity_anchor,
            user_signal=user_signal,
            archive_needed=archive_needed,
            verification_status=verification_status,
        )

    @staticmethod
    def export_state(live_state: LiveState | dict) -> dict[str, object]:
        if isinstance(live_state, dict):
            live_state = LiveState(**live_state)
        return live_state.to_dict()

    @staticmethod
    def _derive_current_axis(
        live_input: LiveStateInput,
        context_view: dict[str, object],
        active_mode: str,
    ) -> str:
        if live_input.current_axis_hint:
            return live_input.current_axis_hint
        task_focus = str(context_view.get("task_focus", ""))
        if task_focus:
            return task_focus
        return f"{active_mode}_axis"

    @staticmethod
    def _derive_tension_flags(
        live_input: LiveStateInput,
        context_view: dict[str, object],
        verification_status: str,
    ) -> list[str]:
        flags: list[str] = []
        if live_input.disagreement_open or str(context_view.get("shared_disagreement_status", "")).startswith("open:"):
            flags.append("open_disagreement")
        if verification_status.lower() in {"pending", "failed", "unknown"}:
            flags.append("verification_unsettled")
        if live_input.monitor_summary and live_input.monitor_summary.get("primary_risk"):
            flags.append(f"monitor:{live_input.monitor_summary['primary_risk']}")
        return flags

    @staticmethod
    def _derive_coherence_level(
        *,
        tension_flags: list[str],
        disagreement_open: bool,
        confidence: float,
    ) -> str:
        if "verification_unsettled" in tension_flags or disagreement_open:
            return "strained"
        if tension_flags or confidence < 0.60:
            return "mixed"
        return "stable"

    @staticmethod
    def _derive_policy_pressure(monitor_summary: dict[str, object] | None) -> str:
        if not monitor_summary:
            return "low"
        level = float(monitor_summary.get("risk_level", 0.0) or 0.0)
        if level >= 0.70:
            return "high"
        if level >= 0.35:
            return "medium"
        return "low"

    @staticmethod
    def _derive_continuity_anchor(live_input: LiveStateInput, context_view: dict[str, object]) -> str:
        if live_input.recent_anchor_cue:
            return live_input.recent_anchor_cue
        if live_input.active_project:
            return live_input.active_project
        return str(context_view.get("active_project", "")) or str(context_view.get("task_focus", ""))

    @staticmethod
    def _derive_archive_needed(tension_flags: list[str], context_view: dict[str, object]) -> bool:
        obligations = context_view.get("open_obligations", [])
        return bool(len(tension_flags) >= 2 and obligations)
