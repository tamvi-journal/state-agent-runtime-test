from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class RuntimeSecurityDecision:
    object_type: str
    trust_stage: str
    can_read_metadata: bool
    can_open_content: bool
    can_execute: bool
    requires_approval: bool
    recommended_zone: str
    risk_summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RuntimeSecurityBoundaries:
    """
    Curious mind, disciplined hands.

    Minimal boundary object for Phase 3.0.
    """

    def classify(
        self,
        *,
        object_type: str,
        trust_stage: str = "unknown",
    ) -> RuntimeSecurityDecision:
        risky_types = {"file", "repo", "package", "script", "doc", "tool_output", "url"}

        if object_type not in risky_types:
            return RuntimeSecurityDecision(
                object_type=object_type,
                trust_stage=trust_stage,
                can_read_metadata=True,
                can_open_content=False,
                can_execute=False,
                requires_approval=True,
                recommended_zone="inspection",
                risk_summary="unknown object type; treat conservatively",
            )

        if trust_stage == "unknown":
            return RuntimeSecurityDecision(
                object_type=object_type,
                trust_stage=trust_stage,
                can_read_metadata=True,
                can_open_content=False,
                can_execute=False,
                requires_approval=True,
                recommended_zone="inspection",
                risk_summary="untrusted object; inspect metadata first",
            )

        if trust_stage == "inspected":
            return RuntimeSecurityDecision(
                object_type=object_type,
                trust_stage=trust_stage,
                can_read_metadata=True,
                can_open_content=True,
                can_execute=False,
                requires_approval=True,
                recommended_zone="sandbox",
                risk_summary="structure reviewed, but execution still blocked",
            )

        if trust_stage == "sandboxed":
            return RuntimeSecurityDecision(
                object_type=object_type,
                trust_stage=trust_stage,
                can_read_metadata=True,
                can_open_content=True,
                can_execute=False,
                requires_approval=True,
                recommended_zone="sandbox",
                risk_summary="tested in sandbox only; host execution still blocked",
            )

        return RuntimeSecurityDecision(
            object_type=object_type,
            trust_stage=trust_stage,
            can_read_metadata=True,
            can_open_content=True,
            can_execute=False,
            requires_approval=True,
            recommended_zone="host",
            risk_summary="narrow approved use only; do not auto-execute",
        )
