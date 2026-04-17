from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


_ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}
_ALLOWED_STATUSES = {"accepted", "rejected"}


@dataclass(slots=True)
class WebhookHttpRequest:
    method: str
    path: str
    headers: dict[str, Any]
    json_body: dict[str, Any]

    def __post_init__(self) -> None:
        if self.method not in _ALLOWED_METHODS:
            raise ValueError(f"invalid method: {self.method}")
        if not self.path.strip():
            raise ValueError("path must be non-empty")
        if not isinstance(self.headers, dict):
            raise ValueError("headers must be a dict")
        if not isinstance(self.json_body, dict):
            raise ValueError("json_body must be a dict")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class WebhookHttpResponse:
    status: str
    http_code: int
    body: dict[str, Any]

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_STATUSES:
            raise ValueError(f"invalid status: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)