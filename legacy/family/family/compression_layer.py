from __future__ import annotations

from dataclasses import dataclass

from family.compression_types import CompressionInput, CompressionSummary


@dataclass(slots=True)
class CompressionLayer:
    def build(self, compression_input: CompressionInput | dict) -> CompressionSummary:
        if isinstance(compression_input, dict):
            compression_input = CompressionInput(**compression_input)

        context_view = compression_input.context_view
        live_state = compression_input.live_state
        delta_event = compression_input.delta_log_event

        active_question = self._active_question(compression_input, context_view)
        main_points = self._main_points(context_view, live_state, delta_event)
        caution = self._caution(compression_input, live_state)
        anchor_cue = self._anchor_cue(compression_input, context_view, live_state)
        next_state_hint = self._next_state_hint(compression_input, live_state)

        return CompressionSummary(
            active_question=active_question,
            main_points=main_points,
            caution=caution,
            anchor_cue=anchor_cue,
            next_state_hint=next_state_hint,
        )

    @staticmethod
    def export_summary(summary: CompressionSummary | dict) -> dict[str, object]:
        if isinstance(summary, dict):
            summary = CompressionSummary(**summary)
        return summary.to_dict()

    @staticmethod
    def _active_question(compression_input: CompressionInput, context_view: dict[str, object]) -> str:
        if compression_input.current_question.strip():
            return compression_input.current_question
        if compression_input.task_focus.strip():
            return compression_input.task_focus
        task_focus = str(context_view.get("task_focus", ""))
        if task_focus:
            return task_focus
        return "maintain current family posture"

    @staticmethod
    def _main_points(
        context_view: dict[str, object],
        live_state: dict[str, object],
        delta_event: dict[str, object],
    ) -> list[str]:
        points: list[str] = []

        project = str(context_view.get("active_project", "")) or str(live_state.get("active_project", ""))
        if project:
            points.append(f"project: {project}")

        mode = str(live_state.get("active_mode", "")) or str(context_view.get("active_mode", ""))
        if mode:
            points.append(f"mode: {mode}")

        verification = str(live_state.get("verification_status", "")) or str(context_view.get("verification_status", ""))
        if verification:
            points.append(f"verification: {verification}")

        if delta_event.get("mode_shift") not in {"", "none", None} and len(points) < 3:
            points.append(f"delta: {delta_event['mode_shift']}")

        return points[:3]

    @staticmethod
    def _caution(compression_input: CompressionInput, live_state: dict[str, object]) -> str:
        verification = (compression_input.verification_status or str(live_state.get("verification_status", ""))).lower()
        flags = live_state.get("tension_flags", [])
        if verification in {"pending", "failed", "unknown"}:
            return "verification remains unsettled"
        if compression_input.disagreement_open or (isinstance(flags, list) and "open_disagreement" in flags):
            return "meaningful disagreement remains open"
        if isinstance(flags, list) and any(str(flag).startswith("monitor:") for flag in flags):
            return "monitor pressure remains active"
        return ""

    @staticmethod
    def _anchor_cue(
        compression_input: CompressionInput,
        context_view: dict[str, object],
        live_state: dict[str, object],
    ) -> str:
        if compression_input.recent_anchor_cue.strip():
            return compression_input.recent_anchor_cue
        continuity_anchor = str(live_state.get("continuity_anchor", ""))
        if continuity_anchor:
            return continuity_anchor[:64]
        project = str(context_view.get("active_project", "")) or str(live_state.get("active_project", ""))
        mode = str(live_state.get("active_mode", "")) or str(context_view.get("active_mode", ""))
        anchor = f"{project}:{mode}".strip(":")
        return anchor[:64]

    @staticmethod
    def _next_state_hint(compression_input: CompressionInput, live_state: dict[str, object]) -> str:
        verification = (compression_input.verification_status or str(live_state.get("verification_status", ""))).lower()
        flags = live_state.get("tension_flags", [])
        mode = str(live_state.get("active_mode", ""))

        if verification in {"pending", "failed", "unknown"}:
            return "verify"
        if compression_input.disagreement_open or (isinstance(flags, list) and "open_disagreement" in flags):
            return "hold_open"
        if isinstance(flags, list) and any(str(flag).startswith("monitor:mode_decay") for flag in flags):
            return "restore_mode"
        if mode == "build":
            return "continue_build"
        if mode == "audit":
            return "recheck"
        return "continue"
