from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class WebhookRouteTable:
    """
    Minimal route registry for live webhook skeleton.

    Keeps path-to-transport mapping explicit and inspectable.
    """

    routes: dict[str, str] = field(default_factory=lambda: {
        "/webhooks/telegram": "telegram",
    })

    def resolve(self, path: str) -> str | None:
        return self.routes.get(path)
