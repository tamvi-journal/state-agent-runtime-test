from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


_ALLOWED_TRANSPORTS = {"telegram", "cli", "http", "operator_console"}
_ALLOWED_STATUS = {"ok", "retryable_error", "fatal_error", "ack"}


@dataclass(slots=True)
class TransportInboundEnvelope:
    transport: str
    transport_message_id: str
    session_id: str
    source_user_id: str
    payload: dict[str, Any]

    def __post_init__(self) -> None:
        if self.transport not in _ALLOWED_TRANSPORTS:
            raise ValueError(f"invalid transport: {self.transport}")
        if not self.transport_message_id.strip():
            raise ValueError("transport_message_id must be non-empty")
        if not self.session_id.strip():
            raise ValueError("session_id must be non-empty")
        if not self.source_user_id.strip():
            raise ValueError("source_user_id must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TransportOutboundEnvelope:
    transport: str
    destination_id: str
    payload: dict[str, Any]
    reply_to_transport_message_id: str | None = None

    def __post_init__(self) -> None:
        if self.transport not in _ALLOWED_TRANSPORTS:
            raise ValueError(f"invalid transport: {self.transport}")
        if not self.destination_id.strip():
            raise ValueError("destination_id must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TransportAck:
    transport: str
    status: str
    reason: str
    transport_message_id: str

    def __post_init__(self) -> None:
        if self.transport not in _ALLOWED_TRANSPORTS:
            raise ValueError(f"invalid transport: {self.transport}")
        if self.status != "ack":
            raise ValueError("TransportAck status must be 'ack'")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TransportError:
    transport: str
    status: str
    reason: str
    retryable: bool
    transport_message_id: str

    def __post_init__(self) -> None:
        if self.transport not in _ALLOWED_TRANSPORTS:
            raise ValueError(f"invalid transport: {self.transport}")
        if self.status not in {"retryable_error", "fatal_error"}:
            raise ValueError("TransportError status must be retryable_error or fatal_error")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
