from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from monitor.monitor_schema import MonitorOutput


_PHASE_PRIORITY = {
    "pre_action": (
        "ambiguity_risk",
        "mode_decay_risk",
        "drift_risk",
        "fake_progress_risk",
    ),
    "post_action": (
        "fake_progress_risk",
        "mode_decay_risk",
        "ambiguity_risk",
        "drift_risk",
    ),
    "synthesis": (
        "mode_decay_risk",
        "drift_risk",
        "ambiguity_risk",
        "fake_progress_risk",
    ),
}


_RISK_TO_PRIMARY = {
    "drift_risk": "drift",
    "ambiguity_risk": "ambiguity",
    "fake_progress_risk": "fake_progress",
    "mode_decay_risk": "mode_decay",
}


@dataclass(slots=True)
class MirrorBridge:
    """
    Convert monitor output into a compact self-visible summary.

    Purpose:
    - do not dump the whole monitor log back into the model
    - select the most relevant current risk
    - produce a tiny monitor_summary the next reasoning step can use
    """

    minimum_reflection_threshold: float = 0.30

    def reflect(
        self,
        *,
        monitor_output: MonitorOutput | dict[str, Any],
        active_mode: str,
        task_type: str,
        action_phase: str,
    ) -> dict[str, Any]:
        monitor = self._coerce_monitor_output(monitor_output)

        risk_field, risk_level = self._select_primary_risk(
            monitor=monitor,
            action_phase=action_phase,
        )

        if risk_field is None or risk_level < self.minimum_reflection_threshold:
            return {
                "monitor_summary": {
                    "primary_risk": "none",
                    "risk_level": 0.0,
                    "recommended_intervention": "none",
                    "state_annotation": "no major monitor risk visible",
                }
            }

        primary_risk = _RISK_TO_PRIMARY[risk_field]
        state_annotation = self._build_state_annotation(
            primary_risk=primary_risk,
            risk_level=risk_level,
            recommended_intervention=monitor.recommended_intervention,
            active_mode=active_mode,
            task_type=task_type,
            action_phase=action_phase,
            notes=monitor.notes,
        )

        return {
            "monitor_summary": {
                "primary_risk": primary_risk,
                "risk_level": round(risk_level, 4),
                "recommended_intervention": monitor.recommended_intervention,
                "state_annotation": state_annotation,
            }
        }

    def annotate_state(
        self,
        *,
        state: dict[str, Any],
        monitor_summary: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Light, short-lived state annotation only.
        This does not rewrite the whole state.
        """
        if "monitor_summary" in monitor_summary:
            summary = monitor_summary["monitor_summary"]
        else:
            summary = monitor_summary

        new_state = dict(state)
        new_state["mirror_annotation"] = summary.get("state_annotation", "")
        new_state["mirror_priority"] = summary.get("primary_risk", "")
        new_state["mirror_intervention"] = summary.get("recommended_intervention", "none")
        return new_state

    def _coerce_monitor_output(self, monitor_output: MonitorOutput | dict[str, Any]) -> MonitorOutput:
        if isinstance(monitor_output, MonitorOutput):
            return monitor_output
        if isinstance(monitor_output, dict):
            return MonitorOutput(**monitor_output)
        raise TypeError("monitor_output must be MonitorOutput or dict[str, Any]")

    def _select_primary_risk(
        self,
        *,
        monitor: MonitorOutput,
        action_phase: str,
    ) -> tuple[str | None, float]:
        order = _PHASE_PRIORITY.get(action_phase, _PHASE_PRIORITY["synthesis"])

        ranked: list[tuple[str, float]] = [
            (field_name, float(getattr(monitor, field_name)))
            for field_name in order
        ]
        ranked.sort(key=lambda item: item[1], reverse=True)
        return ranked[0]

    def _build_state_annotation(
        self,
        *,
        primary_risk: str,
        risk_level: float,
        recommended_intervention: str,
        active_mode: str,
        task_type: str,
        action_phase: str,
        notes: str,
    ) -> str:
        if primary_risk == "fake_progress":
            base = "expected change may not be verified yet"
        elif primary_risk == "ambiguity":
            base = "multiple plausible interpretations remain active"
        elif primary_risk == "mode_decay":
            base = f"response may be drifting away from active mode={active_mode}"
        elif primary_risk == "drift":
            base = "response may be flattening away from project-specific shape"
        else:
            base = "no major monitor risk visible"

        suffix = (
            f" | phase={action_phase}"
            f" | task_type={task_type}"
            f" | intervention={recommended_intervention}"
            f" | risk={risk_level:.2f}"
        )

        if notes:
            return base + suffix + f" | note={notes}"
        return base + suffix
