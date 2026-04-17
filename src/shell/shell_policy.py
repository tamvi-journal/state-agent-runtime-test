from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class ShellPolicyDecision:
    render_mode: str
    trace_allowed: bool
    operator_payload_allowed: bool
    reason: str
    flags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ShellPolicy:
    """
    Minimal shell policy.

    Rules:
    - user channels default to user view
    - trace is not exposed unless explicitly allowed
    - builder/operator surfaces can see more internal state
    """

    def decide(
        self,
        *,
        channel: str,
        requested_mode: str,
        wants_trace: bool,
        wants_builder_view: bool,
    ) -> ShellPolicyDecision:
        flags: list[str] = []

        if channel == "operator":
            flags.append("operator_surface")
            return ShellPolicyDecision(
                render_mode="operator",
                trace_allowed=True,
                operator_payload_allowed=True,
                reason="operator channel may inspect runtime state",
                flags=flags,
            )

        if channel == "debug_console":
            flags.append("debug_surface")
            return ShellPolicyDecision(
                render_mode="builder" if wants_builder_view else "user",
                trace_allowed=True,
                operator_payload_allowed=False,
                reason="debug console may expose trace for builder inspection",
                flags=flags,
            )

        if requested_mode == "builder" or wants_builder_view:
            flags.append("builder_view_requested")
            return ShellPolicyDecision(
                render_mode="builder",
                trace_allowed=wants_trace,
                operator_payload_allowed=False,
                reason="builder view explicitly requested",
                flags=flags,
            )

        flags.append("default_user_surface")
        return ShellPolicyDecision(
            render_mode="user",
            trace_allowed=False,
            operator_payload_allowed=False,
            reason="normal user surface keeps internals hidden",
            flags=flags,
        )
