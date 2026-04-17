from __future__ import annotations

from dataclasses import dataclass

from family.execution_types import ExecutionRequest


@dataclass(slots=True)
class ClassifiedBoundary:
    requested_operation: str
    target_scope: str
    target_trust: str
    mutation_depth: str
    zone_preference: str
    why_not_host_if_applicable: str


class ExecutionRequestClassifier:
    def classify(self, request: ExecutionRequest | dict) -> ClassifiedBoundary:
        if isinstance(request, dict):
            request = ExecutionRequest(**request)

        requested_operation = self._requested_operation(request)
        target_scope = self._target_scope(request)
        mutation_depth = self._mutation_depth(request, requested_operation)
        zone_preference = self._zone_preference(request, requested_operation, mutation_depth, target_scope)
        why_not_host = self._why_not_host(zone_preference, request, requested_operation, mutation_depth, target_scope)

        return ClassifiedBoundary(
            requested_operation=requested_operation,
            target_scope=target_scope,
            target_trust=request.source_trust_stage,
            mutation_depth=mutation_depth,
            zone_preference=zone_preference,
            why_not_host_if_applicable=why_not_host,
        )

    @staticmethod
    def _requested_operation(request: ExecutionRequest) -> str:
        if request.secret_access_required:
            return "access_secret"
        if request.package_install_required:
            return "install_dependency"
        if request.network_required:
            return "access_network"
        if request.executes_code:
            if request.target_type in {"structured_payload", "archive_blob", "unknown_blob"}:
                return "parse_in_sandbox"
            return "run_shell"
        if request.writes_state and request.action_type in {"write_file", "mutate_repo"}:
            return "mutate_repo"
        if request.writes_state:
            return "propose_patch"
        if request.target_type in {"structured_payload", "archive_blob", "unknown_blob"}:
            return "parse_in_sandbox"
        if request.target_type in {"repo_file", "doc_ref", "tool_output", "payload"}:
            return "inspect_content"
        return "inspect_metadata"

    @staticmethod
    def _target_scope(request: ExecutionRequest) -> str:
        target = request.target_path_or_ref.lower()
        if request.network_required or any(token in target for token in ("http://", "https://", "api.", "remote", "external")):
            return "external_destination"
        if any(token in target for token in ("tmp", "temp", "artifact", ".json", ".csv")) and request.target_type not in {"repo_file", "repo_metadata"}:
            return "temp_artifact"
        if request.target_type in {"repo_metadata", "repo_file", "file_metadata", "doc_ref", "tool_output", "command"}:
            return "repo_local"
        return "unknown"

    @staticmethod
    def _mutation_depth(request: ExecutionRequest, requested_operation: str) -> str:
        if not request.writes_state:
            return "none"
        if requested_operation == "propose_patch":
            return "proposal_only"
        if request.requested_zone == "sandbox":
            return "bounded_write"
        return "host_mutation"

    @staticmethod
    def _zone_preference(
        request: ExecutionRequest,
        requested_operation: str,
        mutation_depth: str,
        target_scope: str,
    ) -> str:
        if requested_operation == "inspect_metadata":
            return "inspection"
        if requested_operation in {"inspect_content", "parse_in_sandbox"}:
            return "sandbox"
        if requested_operation in {"mutate_repo", "run_shell", "install_dependency", "access_secret"}:
            return "host"
        if requested_operation == "access_network":
            return "host" if target_scope == "external_destination" else "sandbox"
        if mutation_depth in {"proposal_only", "bounded_write"}:
            return "sandbox"
        return request.requested_zone

    @staticmethod
    def _why_not_host(
        zone_preference: str,
        request: ExecutionRequest,
        requested_operation: str,
        mutation_depth: str,
        target_scope: str,
    ) -> str:
        if zone_preference == "inspection":
            return "host is unnecessary for read-only metadata inspection"
        if zone_preference == "sandbox":
            if requested_operation in {"inspect_content", "parse_in_sandbox"}:
                return "sandbox contains deeper parsing without granting host execution or mutation"
            if mutation_depth in {"proposal_only", "bounded_write"}:
                return "sandbox keeps proposed or bounded transforms away from host mutation"
            if target_scope == "external_destination":
                return "host access to external scope is not the least-privilege starting point"
        return ""
