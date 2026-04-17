from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


_ALLOWED_LEVELS = {"debug", "info", "warning", "error", "critical"}


@dataclass(slots=True)
class LoggingBootstrapResult:
    configured: bool
    log_level: str
    reason: str

    def __post_init__(self) -> None:
        if self.log_level not in _ALLOWED_LEVELS:
            raise ValueError(f"invalid log_level: {self.log_level}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def bootstrap_logging(*, log_level: str) -> LoggingBootstrapResult:
    level = log_level.strip().lower()
    if level not in _ALLOWED_LEVELS:
        level = "info"

    return LoggingBootstrapResult(
        configured=True,
        log_level=level,
        reason="logging bootstrap skeleton configured",
    )
