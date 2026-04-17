from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shell.external_shell import ExternalShell
from shell.operator_snapshot import OperatorSnapshotBuilder
from shell.shell_contract import ShellRequest, ShellResponse


@dataclass(slots=True)
class ShellRuntimeBridge:
    """
    Bridge between an external shell request and an already-produced runtime result.

    This is still not a live Telegram adapter.
    It is the first unified handoff layer:
    shell request -> shell policy -> runtime-visible response/operator view
    """

    external_shell: ExternalShell = field(default_factory=ExternalShell)
    operator_snapshot_builder: OperatorSnapshotBuilder = field(default_factory=OperatorSnapshotBuilder)

    def handle(
        self,
        *,
        shell_request: ShellRequest | dict[str, Any],
        runtime_result: dict[str, Any],
    ) -> dict[str, Any]:
        response = self.external_shell.handle(
            shell_request=shell_request,
            runtime_result=runtime_result,
        )

        if isinstance(shell_request, dict):
            shell_request = ShellRequest(**shell_request)

        operator_snapshot = None
        if response.operator_payload is not None:
            operator_snapshot = self.operator_snapshot_builder.build(
                runtime_result=runtime_result,
            )

        return {
            "shell_request": shell_request.to_dict(),
            "shell_response": response.to_dict(),
            "operator_snapshot": operator_snapshot,
        }
