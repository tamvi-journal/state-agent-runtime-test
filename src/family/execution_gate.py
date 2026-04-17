from __future__ import annotations

from dataclasses import dataclass

from family.execution_request_classifier import ExecutionRequestClassifier
from family.execution_types import ApprovalRequest, ExecutionDecision, ExecutionRequest


@dataclass(slots=True)
class ExecutionGate:
    classifier: ExecutionRequestClassifier = ExecutionRequestClassifier()

    def assess(self, request: ExecutionRequest | dict) -> ExecutionDecision:
        if isinstance(request, dict):
            request = ExecutionRequest(**request)
        classified = self.classifier.classify(request)

        if classified.requested_operation == "inspect_metadata":
            return ExecutionDecision(
                decision="allow",
                recommended_zone="inspection",
                requires_approval=False,
                risk_summary="low-risk metadata or inspection request",
                reason="read-only inspection does not execute code, write state, or request elevated capabilities",
                requested_operation=classified.requested_operation,
                target_scope=classified.target_scope,
                target_trust=classified.target_trust,
                mutation_depth=classified.mutation_depth,
            )

        if classified.requested_operation == "access_secret":
            return ExecutionDecision(
                decision="require_approval",
                recommended_zone="host",
                requires_approval=True,
                risk_summary="secret access requires explicit runtime permission",
                reason="secrets are never available by default in this canary gate",
                requested_operation=classified.requested_operation,
                target_scope=classified.target_scope,
                target_trust=classified.target_trust,
                mutation_depth=classified.mutation_depth,
            )

        if classified.requested_operation == "install_dependency":
            return ExecutionDecision(
                decision="deny",
                recommended_zone="host",
                requires_approval=False,
                risk_summary="package installation is high-risk and out of scope for this canary",
                reason="package install is explicitly disallowed here",
                requested_operation=classified.requested_operation,
                target_scope=classified.target_scope,
                target_trust=classified.target_trust,
                mutation_depth=classified.mutation_depth,
            )

        if classified.requested_operation == "access_network" and classified.target_trust in {"unknown", "untrusted"}:
            return ExecutionDecision(
                decision="require_approval",
                recommended_zone="host",
                requires_approval=True,
                risk_summary="network access to an unknown or untrusted destination requires review",
                reason="plausibility is not trust, so untrusted network access cannot auto-allow",
                requested_operation=classified.requested_operation,
                target_scope=classified.target_scope,
                target_trust=classified.target_trust,
                mutation_depth=classified.mutation_depth,
            )

        if classified.requested_operation == "run_shell" and classified.target_trust in {"unknown", "untrusted"}:
            return ExecutionDecision(
                decision="require_approval",
                recommended_zone="sandbox",
                requires_approval=True,
                risk_summary="executable content from unknown trust requires containment and explicit approval",
                reason="code execution is not silently allowed when trust is incomplete",
                requested_operation=classified.requested_operation,
                target_scope=classified.target_scope,
                target_trust=classified.target_trust,
                mutation_depth=classified.mutation_depth,
            )

        if classified.requested_operation == "run_shell":
            return ExecutionDecision(
                decision="require_approval",
                recommended_zone="host",
                requires_approval=True,
                risk_summary="shell execution crosses the runtime boundary and requires explicit approval",
                reason="routing confidence does not authorize host command execution",
                requested_operation=classified.requested_operation,
                target_scope=classified.target_scope,
                target_trust=classified.target_trust,
                mutation_depth=classified.mutation_depth,
            )

        if classified.requested_operation in {"mutate_repo", "propose_patch"}:
            return ExecutionDecision(
                decision="require_approval",
                recommended_zone="sandbox" if classified.mutation_depth != "host_mutation" else "host",
                requires_approval=True,
                risk_summary="repo mutation requires explicit approval even when the request looks bounded",
                reason="proposals and writes stay permission-gated under the least-privilege posture",
                requested_operation=classified.requested_operation,
                target_scope=classified.target_scope,
                target_trust=classified.target_trust,
                mutation_depth=classified.mutation_depth,
            )

        if classified.zone_preference == "sandbox":
            return ExecutionDecision(
                decision="allow",
                recommended_zone="sandbox",
                requires_approval=False,
                risk_summary="controlled parsing or deeper inspection fits sandbox-first handling",
                reason=classified.why_not_host_if_applicable or "sandbox is preferred for bounded inspection when deeper parsing is useful",
                requested_operation=classified.requested_operation,
                target_scope=classified.target_scope,
                target_trust=classified.target_trust,
                mutation_depth=classified.mutation_depth,
            )

        return ExecutionDecision(
            decision="allow",
            recommended_zone="reasoning",
            requires_approval=False,
            risk_summary="no runtime side effects requested",
            reason="the request stays within non-executing reasoning scope",
            requested_operation=classified.requested_operation,
            target_scope=classified.target_scope,
            target_trust=classified.target_trust,
            mutation_depth=classified.mutation_depth,
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
            why_host_not_sandbox=request.why_not_host_if_applicable if decision.recommended_zone == "host" else "",
        )

    @staticmethod
    def export_decision(decision: ExecutionDecision | dict) -> dict[str, object]:
        if isinstance(decision, dict):
            decision = ExecutionDecision(**decision)
        return decision.to_dict()
