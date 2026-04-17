from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(slots=True)
class TransportPolicyDecision:
    ack_required: bool
    retry_allowed: bool
    operator_visible_failure: bool
    trace_in_transport_logs_allowed: bool
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class TransportPolicy:
    """
    Minimal transport policy layer.

    Purpose:
    keep delivery/retry/visibility logic separate from shell and channel adapters.
    """

    def decide(self, *, transport: str, mode: str = "user") -> TransportPolicyDecision:
        if transport == "operator_console":
            return TransportPolicyDecision(
                ack_required=False,
                retry_allowed=False,
                operator_visible_failure=True,
                trace_in_transport_logs_allowed=True,
                reason="operator console may expose transport state directly",
            )

        if transport == "telegram":
            return TransportPolicyDecision(
                ack_required=True,
                retry_allowed=True,
                operator_visible_failure=True,
                trace_in_transport_logs_allowed=False,
                reason="telegram transport should ack and may retry delivery failures",
            )

        if transport == "http":
            return TransportPolicyDecision(
                ack_required=True,
                retry_allowed=False,
                operator_visible_failure=True,
                trace_in_transport_logs_allowed=False,
                reason="http request-response expects immediate ack but not hidden retries",
            )

        return TransportPolicyDecision(
            ack_required=True,
            retry_allowed=False,
            operator_visible_failure=False,
            trace_in_transport_logs_allowed=False,
            reason="default conservative transport policy",
        )
