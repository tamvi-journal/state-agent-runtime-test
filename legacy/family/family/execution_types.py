from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


DecisionKind = Literal["allow", "deny", "require_approval"]
RuntimeZone = Literal["reasoning", "inspection", "sandbox", "host"]
TrustStage = Literal["trusted", "reviewed", "unknown", "untrusted"]
RequestedOperation = Literal[
    "inspect_metadata",
    "inspect_content",
    "parse_in_sandbox",
    "propose_patch",
    "mutate_repo",
    "run_shell",
    "install_dependency",
    "access_secret",
    "access_network",
]
TargetScope = Literal["repo_local", "temp_artifact", "external_destination", "unknown"]
MutationDepth = Literal["none", "proposal_only", "bounded_write", "host_mutation"]

_ALLOWED_DECISIONS = {"allow", "deny", "require_approval"}
_ALLOWED_ZONES = {"reasoning", "inspection", "sandbox", "host"}
_ALLOWED_TRUST = {"trusted", "reviewed", "unknown", "untrusted"}
_ALLOWED_OPERATIONS = {
    "inspect_metadata",
    "inspect_content",
    "parse_in_sandbox",
    "propose_patch",
    "mutate_repo",
    "run_shell",
    "install_dependency",
    "access_secret",
    "access_network",
}
_ALLOWED_TARGET_SCOPES = {"repo_local", "temp_artifact", "external_destination", "unknown"}
_ALLOWED_MUTATION_DEPTHS = {"none", "proposal_only", "bounded_write", "host_mutation"}


@dataclass(slots=True)
class ExecutionRequest:
    action_type: str
    target_type: str
    target_path_or_ref: str = ""
    requested_zone: RuntimeZone = "reasoning"
    writes_state: bool = False
    executes_code: bool = False
    network_required: bool = False
    package_install_required: bool = False
    secret_access_required: bool = False
    source_trust_stage: TrustStage = "unknown"
    requested_operation: RequestedOperation = "inspect_metadata"
    target_scope: TargetScope = "unknown"
    mutation_depth: MutationDepth = "none"
    zone_preference: RuntimeZone = "reasoning"
    why_not_host_if_applicable: str = ""
    reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.action_type, str) or not self.action_type.strip():
            raise ValueError("action_type must be a non-empty string")
        if not isinstance(self.target_type, str) or not self.target_type.strip():
            raise ValueError("target_type must be a non-empty string")
        if not isinstance(self.target_path_or_ref, str):
            raise TypeError("target_path_or_ref must be a string")
        if self.requested_zone not in _ALLOWED_ZONES:
            raise ValueError(f"requested_zone must be one of: {sorted(_ALLOWED_ZONES)}")
        if self.zone_preference not in _ALLOWED_ZONES:
            raise ValueError(f"zone_preference must be one of: {sorted(_ALLOWED_ZONES)}")
        if self.source_trust_stage not in _ALLOWED_TRUST:
            raise ValueError(f"source_trust_stage must be one of: {sorted(_ALLOWED_TRUST)}")
        if self.requested_operation not in _ALLOWED_OPERATIONS:
            raise ValueError(f"requested_operation must be one of: {sorted(_ALLOWED_OPERATIONS)}")
        if self.target_scope not in _ALLOWED_TARGET_SCOPES:
            raise ValueError(f"target_scope must be one of: {sorted(_ALLOWED_TARGET_SCOPES)}")
        if self.mutation_depth not in _ALLOWED_MUTATION_DEPTHS:
            raise ValueError(f"mutation_depth must be one of: {sorted(_ALLOWED_MUTATION_DEPTHS)}")
        for name in (
            "writes_state",
            "executes_code",
            "network_required",
            "package_install_required",
            "secret_access_required",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool")
        for name in ("reason", "why_not_host_if_applicable"):
            if not isinstance(getattr(self, name), str):
                raise TypeError(f"{name} must be a string")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ExecutionDecision:
    decision: DecisionKind
    recommended_zone: RuntimeZone
    requires_approval: bool
    risk_summary: str
    reason: str
    requested_operation: RequestedOperation = "inspect_metadata"
    target_scope: TargetScope = "unknown"
    target_trust: TrustStage = "unknown"
    mutation_depth: MutationDepth = "none"

    def __post_init__(self) -> None:
        if self.decision not in _ALLOWED_DECISIONS:
            raise ValueError(f"decision must be one of: {sorted(_ALLOWED_DECISIONS)}")
        if self.recommended_zone not in _ALLOWED_ZONES:
            raise ValueError(f"recommended_zone must be one of: {sorted(_ALLOWED_ZONES)}")
        if not isinstance(self.requires_approval, bool):
            raise TypeError("requires_approval must be a bool")
        if not isinstance(self.risk_summary, str):
            raise TypeError("risk_summary must be a string")
        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string")
        if self.requested_operation not in _ALLOWED_OPERATIONS:
            raise ValueError(f"requested_operation must be one of: {sorted(_ALLOWED_OPERATIONS)}")
        if self.target_scope not in _ALLOWED_TARGET_SCOPES:
            raise ValueError(f"target_scope must be one of: {sorted(_ALLOWED_TARGET_SCOPES)}")
        if self.target_trust not in _ALLOWED_TRUST:
            raise ValueError(f"target_trust must be one of: {sorted(_ALLOWED_TRUST)}")
        if self.mutation_depth not in _ALLOWED_MUTATION_DEPTHS:
            raise ValueError(f"mutation_depth must be one of: {sorted(_ALLOWED_MUTATION_DEPTHS)}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ApprovalRequest:
    requested_action: str
    why_needed: str
    risk_summary: str
    sandbox_alternative_available: bool
    why_host_not_sandbox: str = ""
    approved: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.requested_action, str) or not self.requested_action.strip():
            raise ValueError("requested_action must be a non-empty string")
        if not isinstance(self.why_needed, str):
            raise TypeError("why_needed must be a string")
        if not isinstance(self.risk_summary, str):
            raise TypeError("risk_summary must be a string")
        if not isinstance(self.sandbox_alternative_available, bool):
            raise TypeError("sandbox_alternative_available must be a bool")
        if not isinstance(self.why_host_not_sandbox, str):
            raise TypeError("why_host_not_sandbox must be a string")
        if not isinstance(self.approved, bool):
            raise TypeError("approved must be a bool")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
