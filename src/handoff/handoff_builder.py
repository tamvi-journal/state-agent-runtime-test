from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from handoff.baton import HandoffBaton


@dataclass(slots=True)
class HandoffBuilder:
    """
    Builds one compact baton from the current turn result.
    """

    def build(
        self,
        *,
        task_focus: str,
        active_mode: str,
        verification_status: str,
        monitor_summary: dict[str, Any],
        next_hint: str,
    ) -> HandoffBaton:
        open_loops = self._infer_open_loops(
            verification_status=verification_status,
            monitor_summary=monitor_summary,
            next_hint=next_hint,
        )
        return HandoffBaton(
            task_focus=task_focus,
            active_mode=active_mode,
            open_loops=open_loops,
            verification_status=verification_status,
            monitor_summary=dict(monitor_summary),
            next_hint=next_hint,
        )

    @staticmethod
    def _infer_open_loops(
        *,
        verification_status: str,
        monitor_summary: dict[str, Any],
        next_hint: str,
    ) -> list[str]:
        loops: list[str] = []

        if verification_status in {"pending", "unknown"}:
            loops.append("verification remains open")

        primary_risk = str(monitor_summary.get("primary_risk", "none"))
        if primary_risk not in {"", "none"}:
            loops.append(f"monitor:{primary_risk}")

        if next_hint.strip():
            loops.append(next_hint.strip())

        return loops

