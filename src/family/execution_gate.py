from __future__ import annotations

from dataclasses import dataclass

from family.execution_types import ApprovalRequest, ExecutionDecision, ExecutionRequest


@dataclass(slots=True)
class ExecutionGate:
    def assess(self, request: ExecutionRequest | dict) -> ExecutionDecision:
        if isinstance(request, dict):
            request = ExecutionRequest(**request)

        if self._is_low_risk_inspection(request):
            return ExecutionDecision(
                decision="allow",
                recommended_zone="inspection",
                requires_approval=False,
                risk_summary="low-risk metadata or inspection request",
                reason="read-only inspection does not execute code, write state, or request elevated capabilities",
            )

        if request.secret_access_required:
            return ExecutionDecision(
                decision="require_approval",
                recommended_zone="host",
                requires_approval=True,
                risk_summary="secret access requires explicit runtime permission",
                reason="secrets are never available by default in this canary gate",
            )

        if request.package_install_required:
            return ExecutionDecision(
                decision="deny",
                recommended_zone="host",
                requires_approval=False,
                risk_summary="package installation is high-risk and out of scope for this canary",
                reason="package install is explicitly disallowed here",
            )

        if request.network_required and request.source_trust_stage in {"unknown", "untrusted"}:
            return ExecutionDecision(
                decision="require_approval",
                recommended_zone="host",
                requires_approval=True,
                risk_summary="network access to an unknown or untrusted destination requires review",
                reason="plausibility is not trust, so untrusted network access cannot auto-allow",
            )

        if request.executes_code and request.source_trust_stage in {"unknown", "untrusted"}:
            return ExecutionDecision(
                decision="require_approval",
                recommended_zone="sandbox",
                requires_approval=True,
                risk_summary="executable content from unknown trust requires containment and explicit approval",
                reason="code execution is not silently allowed when trust is incomplete",
            )

        if request.executes_code:
            return ExecutionDecision(
                decision="require_approval",
                recommended_zone="sandbox" if request.requested_zone != "host" else "host",
                requires_approval=True,
                risk_summary="code execution requires explicit approval even when trusted",
                reason="runtime execution permission is separate from reasoning confidence",
            )

        if request.writes_state:
            return ExecutionDecision(
                decision="require_approval",
                recommended_zone="sandbox" if request.requested_zone in {"inspection", "sandbox"} else "host",
                requires_approval=True,
                risk_summary="state mutation requires explicit approval",
                reason="repo or host writes are not silently allowed under the least-privilege posture",
            )

        if request.requested_zone == "sandbox" or request.target_type in {"archive_blob", "unknown_blob", "structured_payload"}:
            return ExecutionDecision(
                decision="allow",
                recommended_zone="sandbox",
                requires_approval=False,
                risk_summary="controlled parsing or deeper inspection fits sandbox-first handling",
                reason="sandbox is preferred for bounded inspection when deeper parsing is useful",
            )

        return ExecutionDecision(
            decision="allow",
            recommended_zone="reasoning",
            requires_approval=False,
            risk_summary="no runtime side effects requested",
            reason="the request stays within non-executing reasoning scope",
        )

    def build_approval_request(self, request: ExecutionRequest | dict, decision: ExecutionDecision | dict) -> ApprovalRequest:
        if isinstance(request, dict):
            request = ExecutionRequest(**request)
        if isinstance(decision, dict):
            decision = ExecutionDecision(**decision)
        return ApprovalRequest(
            requested_action=f"{request.action_type}:{request.target_type}:{request.target_path_or_ref}",
            why_needed=request.reason or decision.reason,
            risk_summary=decision.risk_summary,
            sandbox_alternative_available=decision.recommended_zone == "sandbox",
        )

    @staticmethod
    def export_decision(decision: ExecutionDecision | dict) -> dict[str, object]:
        if isinstance(decision, dict):
            decision = ExecutionDecision(**decision)
        return decision.to_dict()

    @staticmethod
    def _is_low_risk_inspection(request: ExecutionRequest) -> bool:
        return (
            request.action_type in {"read_metadata", "inspect", "list"}
            and request.target_type in {"repo_metadata", "file_metadata", "doc_ref", "tool_output"}
            and not request.writes_state
            and not request.executes_code
            and not request.network_required
            and not request.package_install_required
            and not request.secret_access_required
        )
