from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


_ALLOWED_CHANNELS = {"chat", "telegram", "debug_console", "operator"}
_ALLOWED_MODES = {"user", "builder", "operator"}


@dataclass(slots=True)
class ShellRequest:
    channel: str
    user_text: str
    user_id: str
    session_id: str
    requested_mode: str = "user"
    wants_trace: bool = False
    wants_builder_view: bool = False

    def __post_init__(self) -> None:
        if self.channel not in _ALLOWED_CHANNELS:
            raise ValueError(f"invalid channel: {self.channel}")
        if self.requested_mode not in _ALLOWED_MODES:
            raise ValueError(f"invalid requested_mode: {self.requested_mode}")
        if not self.user_text.strip():
            raise ValueError("user_text must be non-empty")
        if not self.user_id.strip():
            raise ValueError("user_id must be non-empty")
        if not self.session_id.strip():
            raise ValueError("session_id must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ShellResponse:
    visible_response: str
    render_mode: str
    trace_allowed: bool
    trace_payload: dict[str, Any] | None
    operator_payload: dict[str, Any] | None
    shell_flags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
