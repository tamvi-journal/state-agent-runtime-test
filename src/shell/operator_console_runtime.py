from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shell.operator_console_bridge import OperatorConsoleBridge
from shell.operator_console_renderer import OperatorConsoleRenderer


@dataclass(slots=True)
class OperatorConsoleRuntime:
    """
    Small end-to-end operator console runtime.

    Inputs:
    - runtime_result
    - events
    - optional context/governance/worker artifacts

    Outputs:
    - structured console payload
    - rendered operator text
    """

    bridge: OperatorConsoleBridge = field(default_factory=OperatorConsoleBridge)
    renderer: OperatorConsoleRenderer = field(default_factory=OperatorConsoleRenderer)

    def run(
        self,
        *,
        runtime_result: dict[str, Any],
        events: list[dict[str, Any]],
        context_view: dict[str, Any] | None = None,
        governance_output: dict[str, Any] | None = None,
        worker_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = self.bridge.build(
            runtime_result=runtime_result,
            events=events,
            context_view=context_view,
            governance_output=governance_output,
            worker_payload=worker_payload,
        )
        rendered = self.renderer.render(console_payload=payload)
        return {
            "console_payload": payload,
            "rendered_text": rendered,
        }
