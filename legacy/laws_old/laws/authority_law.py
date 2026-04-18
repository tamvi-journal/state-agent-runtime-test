from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class AuthorityDecision:
    allowed: bool
    authority_holder: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AuthorityLaw:
    """
    Main brain remains synthesis authority.
    Workers, children, and tools can influence but cannot become final authority.
    """

    def evaluate(
        self,
        *,
        actor: str,
        requested_action: str,
    ) -> AuthorityDecision:
        if actor == "main_brain":
            return AuthorityDecision(
                allowed=True,
                authority_holder="main_brain",
                reason="main brain is the designated synthesis authority",
            )

        if actor in {"worker", "tracey", "seyn", "tool"}:
            return AuthorityDecision(
                allowed=False,
                authority_holder="main_brain",
                reason=f"{actor} may advise or provide capability but cannot hold final synthesis authority",
            )

        return AuthorityDecision(
            allowed=False,
            authority_holder="main_brain",
            reason="unknown actor cannot assume synthesis authority",
        )
