from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from observability.dashboard_snapshot import DashboardSnapshotBuilder
from observability.dashboard_summary import DashboardSummaryBuilder
from observability.timeline_view import TimelineViewBuilder
from shell.operator_console_runtime import OperatorConsoleRuntime
from shell.operator_console_session import OperatorConsoleSession
from server.operator_debug_contract import DebugPayload, OperatorPayload
from server.runtime_provider import RuntimeProvider


@dataclass(slots=True)
class OperatorDebugProvider:
    """
    Local operator/debug provider.

    Builds runtime-backed operator and debug payloads from the local runtime provider.
    """

    runtime_provider: RuntimeProvider = field(default_factory=RuntimeProvider)
    operator_console_runtime: OperatorConsoleRuntime = field(default_factory=OperatorConsoleRuntime)
    session: OperatorConsoleSession = field(default_factory=lambda: OperatorConsoleSession(session_id="local-operator"))
    dashboard_builder: DashboardSnapshotBuilder = field(
        default_factory=lambda: DashboardSnapshotBuilder(
            summary_builder=DashboardSummaryBuilder(),
            timeline_builder=TimelineViewBuilder(),
        )
    )

    def get_operator_payload(self, *, user_text: str = "Tracey, this is home.") -> OperatorPayload:
        runtime_result = self.runtime_provider.get_runtime_result(user_text=user_text)
        events = self._build_events_from_runtime(runtime_result)

        console = self.operator_console_runtime.run(
            runtime_result=runtime_result,
            events=events,
            context_view=runtime_result.get("context_view"),
            governance_output=runtime_result.get("governance_output"),
            worker_payload=runtime_result.get("worker_payload"),
        )

        snapshot = console["console_payload"]["operator_snapshot"]
        self.session.append(snapshot)

        return OperatorPayload(
            operator_snapshot=snapshot,
            dashboard_snapshot=console["console_payload"]["dashboard_snapshot"],
            rendered_console=console["rendered_text"],
        )

    def get_debug_payload(self, *, user_text: str = "hello there") -> DebugPayload:
        runtime_result = self.runtime_provider.get_runtime_result(user_text=user_text)

        runtime_shape = {
            "has_final_response": "final_response" in runtime_result,
            "has_routing": "routing" in runtime_result,
            "has_reconciliation": "reconciliation" in runtime_result,
            "has_child_result": "child_result" in runtime_result,
            "has_governance_output": "governance_output" in runtime_result,
            "has_context_view": "context_view" in runtime_result,
            "has_worker_payload": runtime_result.get("worker_payload") is not None,
            "routing": runtime_result.get("routing"),
            "reconciliation": runtime_result.get("reconciliation"),
        }

        return DebugPayload(
            runtime_shape=runtime_shape,
            notes=[
                "debug payload is local-only and intended for builder/operator inspection",
                "runtime shape does not expose raw internal trace by default",
            ],
        )

    def latest_operator_session_summary(self) -> dict[str, Any]:
        return self.session.summary()

    @staticmethod
    def _build_events_from_runtime(runtime_result: dict[str, Any]) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []

        context_view = runtime_result.get("context_view")
        if context_view is not None:
            events.append(
                {
                    "timestamp_utc": "local-now",
                    "category": "context_view",
                    "payload": context_view,
                }
            )

        governance_output = runtime_result.get("governance_output")
        if governance_output is not None:
            events.append(
                {
                    "timestamp_utc": "local-now",
                    "category": "governance_pass",
                    "payload": governance_output,
                }
            )

        child_result = runtime_result.get("child_result", {})
        tracey_turn = child_result.get("tracey_result", {}).get("tracey_turn")
        if tracey_turn is not None:
            events.append(
                {
                    "timestamp_utc": "local-now",
                    "category": "tracey_turn",
                    "payload": tracey_turn,
                }
            )

        seyn_turn = child_result.get("seyn_result", {}).get("seyn_turn")
        if seyn_turn is not None:
            events.append(
                {
                    "timestamp_utc": "local-now",
                    "category": "seyn_turn",
                    "payload": seyn_turn,
                }
            )

        disagreement_result = child_result.get("disagreement_result")
        if disagreement_result is not None:
            events.append(
                {
                    "timestamp_utc": "local-now",
                    "category": "disagreement_event",
                    "payload": disagreement_result,
                }
            )

        reconciliation = runtime_result.get("reconciliation")
        if reconciliation is not None:
            events.append(
                {
                    "timestamp_utc": "local-now",
                    "category": "reconciliation_result",
                    "payload": {"reconciliation": reconciliation},
                }
            )

        return events
