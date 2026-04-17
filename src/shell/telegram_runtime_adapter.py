from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shell.shell_runtime_bridge import ShellRuntimeBridge
from shell.telegram_adapter import TelegramAdapter
from shell.telegram_contract import TelegramInboundMessage


@dataclass(slots=True)
class TelegramRuntimeAdapter:
    """
    Thin end-to-end adapter:
    Telegram inbound -> shell request -> shell runtime bridge -> Telegram outbound

    Still no network calls.
    This is the last clean internal layer before a real bot transport.
    """

    telegram_adapter: TelegramAdapter = field(default_factory=TelegramAdapter)
    shell_runtime_bridge: ShellRuntimeBridge = field(default_factory=ShellRuntimeBridge)

    def handle(
        self,
        *,
        inbound: TelegramInboundMessage | dict[str, Any],
        runtime_result: dict[str, Any],
    ) -> dict[str, Any]:
        if isinstance(inbound, dict):
            inbound = TelegramInboundMessage(**inbound)

        shell_request = self.telegram_adapter.inbound_to_shell_request(
            inbound=inbound,
        )
        shell_payload = self.shell_runtime_bridge.handle(
            shell_request=shell_request,
            runtime_result=runtime_result,
        )
        outbound = self.telegram_adapter.shell_payload_to_outbound(
            inbound=inbound,
            shell_payload=shell_payload,
        )

        return {
            "shell_request": shell_request.to_dict(),
            "shell_payload": shell_payload,
            "telegram_outbound": outbound.to_dict(),
        }
