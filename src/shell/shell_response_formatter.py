from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ShellResponseFormatter:
    """
    Small formatter for shell-facing surfaces.

    Keeps user-facing output, builder-facing output, and operator-facing output
    visually distinct without changing runtime truth.
    """

    def format(self, *, shell_payload: dict[str, Any]) -> dict[str, str]:
        shell_response = shell_payload.get("shell_response", {})
        operator_snapshot = shell_payload.get("operator_snapshot")

        visible = str(shell_response.get("visible_response", ""))
        render_mode = str(shell_response.get("render_mode", "user"))

        if render_mode == "operator" and operator_snapshot is not None:
            operator_text = (
                f"[operator] lead={operator_snapshot.get('lead_brain_for_action')} | "
                f"support={operator_snapshot.get('support_brain')} | "
                f"hold={operator_snapshot.get('hold_for_more_input')} | "
                f"reconciliation={operator_snapshot.get('reconciliation_state')}"
            )
            return {
                "surface_text": visible,
                "operator_text": operator_text,
            }

        if render_mode == "builder":
            trace_allowed = shell_response.get("trace_allowed", False)
            builder_text = f"[builder] trace_allowed={trace_allowed}"
            return {
                "surface_text": visible,
                "operator_text": builder_text,
            }

        return {
            "surface_text": visible,
            "operator_text": "",
        }
