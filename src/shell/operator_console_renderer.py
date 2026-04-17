from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class OperatorConsoleRenderer:
    """
    Render a compact operator-facing text block from the console bridge payload.
    """

    def render(self, *, console_payload: dict[str, Any]) -> str:
        operator_snapshot = console_payload.get("operator_snapshot", {})
        dashboard_snapshot = console_payload.get("dashboard_snapshot", {})

        lines: list[str] = []
        lines.append("[operator-console]")
        lines.append(
            "lead={lead} | support={support} | hold={hold} | surface_disagreement={surface}".format(
                lead=operator_snapshot.get("lead_brain_for_action"),
                support=operator_snapshot.get("support_brain"),
                hold=operator_snapshot.get("hold_for_more_input"),
                surface=operator_snapshot.get("surface_disagreement_to_user"),
            )
        )

        disagreement = dashboard_snapshot.get("disagreement", {})
        reconciliation = dashboard_snapshot.get("reconciliation", {})
        lines.append(
            "disagreement_detected={detected} | still_open={open_} | reconciliation_state={state}".format(
                detected=disagreement.get("detected"),
                open_=disagreement.get("still_open"),
                state=reconciliation.get("state"),
            )
        )

        flags = dashboard_snapshot.get("integrity_flags", [])
        if flags:
            lines.append("flags=" + ", ".join(flags))
        else:
            lines.append("flags=none")

        timeline = dashboard_snapshot.get("timeline", [])
        if timeline:
            lines.append("timeline_head=" + timeline[0].get("summary", ""))

        return "\n".join(lines)
