from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shell.shell_contract import ShellRequest, ShellResponse
from shell.shell_policy import ShellPolicy


@dataclass(slots=True)
class ExternalShell:
    """
    Thin shell around the runtime.

    It does not implement the whole runtime itself.
    It decides what the outside world is allowed to see.
    """

    shell_policy: ShellPolicy = field(default_factory=ShellPolicy)

    def handle(
        self,
        *,
        shell_request: ShellRequest | dict[str, Any],
        runtime_result: dict[str, Any],
    ) -> ShellResponse:
        if isinstance(shell_request, dict):
            shell_request = ShellRequest(**shell_request)

        policy = self.shell_policy.decide(
            channel=shell_request.channel,
            requested_mode=shell_request.requested_mode,
            wants_trace=shell_request.wants_trace,
            wants_builder_view=shell_request.wants_builder_view,
        )

        visible_response = self._select_visible_response(
            runtime_result=runtime_result,
            render_mode=policy.render_mode,
        )

        trace_payload = runtime_result if policy.trace_allowed else None
        operator_payload = self._build_operator_payload(runtime_result) if policy.operator_payload_allowed else None

        return ShellResponse(
            visible_response=visible_response,
            render_mode=policy.render_mode,
            trace_allowed=policy.trace_allowed,
            trace_payload=trace_payload,
            operator_payload=operator_payload,
            shell_flags=policy.flags,
        )

    def _select_visible_response(self, *, runtime_result: dict[str, Any], render_mode: str) -> str:
        if render_mode == "operator":
            return str(runtime_result.get("final_response", ""))
        if render_mode == "builder":
            if "final_response" in runtime_result:
                return str(runtime_result["final_response"])
            return str(runtime_result.get("base_response", ""))
        return str(runtime_result.get("final_response", ""))

    @staticmethod
    def _build_operator_payload(runtime_result: dict[str, Any]) -> dict[str, Any]:
        child_result = runtime_result.get("child_result", {})
        return {
            "routing": runtime_result.get("routing"),
            "reconciliation": runtime_result.get("reconciliation"),
            "disagreement_result": child_result.get("disagreement_result"),
            "tracey_turn": child_result.get("tracey_result", {}).get("tracey_turn"),
            "seyn_turn": child_result.get("seyn_result", {}).get("seyn_turn"),
        }
