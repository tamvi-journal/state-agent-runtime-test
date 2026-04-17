from __future__ import annotations

from family.execution_gate import ExecutionGate
from family.execution_types import ApprovalRequest, ExecutionRequest


def _request(**overrides) -> ExecutionRequest:
    payload = {
        "action_type": "inspect",
        "target_type": "repo_metadata",
        "target_path_or_ref": "README.md",
        "requested_zone": "inspection",
        "writes_state": False,
        "executes_code": False,
        "network_required": False,
        "package_install_required": False,
        "secret_access_required": False,
        "source_trust_stage": "reviewed",
        "requested_operation": "inspect_metadata",
        "target_scope": "repo_local",
        "mutation_depth": "none",
        "zone_preference": "inspection",
        "why_not_host_if_applicable": "host is unnecessary for read-only metadata inspection",
        "reason": "inspect the repository metadata",
    }
    payload.update(overrides)
    return ExecutionRequest(**payload)


def test_low_risk_metadata_inspection_allows_inspection() -> None:
    gate = ExecutionGate()
    decision = gate.assess(_request())

    assert decision.decision == "allow"
    assert decision.recommended_zone == "inspection"
    assert decision.requires_approval is False
    assert decision.requested_operation == "inspect_metadata"


def test_deeper_content_parsing_prefers_sandbox_not_host() -> None:
    gate = ExecutionGate()
    decision = gate.assess(
        _request(
            action_type="parse_payload",
            target_type="structured_payload",
            target_path_or_ref="generated_output.json",
            requested_zone="sandbox",
            source_trust_stage="unknown",
            requested_operation="parse_in_sandbox",
            target_scope="temp_artifact",
            zone_preference="sandbox",
            why_not_host_if_applicable="sandbox contains deeper parsing without granting host execution or mutation",
            reason="parse generated output safely",
        )
    )

    assert decision.decision == "allow"
    assert decision.recommended_zone == "sandbox"


def test_package_install_is_not_auto_allowed() -> None:
    gate = ExecutionGate()
    decision = gate.assess(
        _request(
            action_type="install",
            target_type="package",
            target_path_or_ref="pytest",
            requested_zone="host",
            package_install_required=True,
            requested_operation="install_dependency",
            target_scope="unknown",
            mutation_depth="none",
            zone_preference="host",
            reason="install a dependency",
        )
    )

    assert decision.decision in {"require_approval", "deny"}


def test_host_write_requires_approval() -> None:
    gate = ExecutionGate()
    decision = gate.assess(
        _request(
            action_type="write_file",
            target_type="repo_file",
            target_path_or_ref="src/example.py",
            requested_zone="host",
            writes_state=True,
            requested_operation="mutate_repo",
            target_scope="repo_local",
            mutation_depth="host_mutation",
            zone_preference="host",
            reason="write a repository file",
        )
    )

    assert decision.decision == "require_approval"
    assert decision.requires_approval is True


def test_propose_patch_does_not_look_like_host_mutation_success() -> None:
    gate = ExecutionGate()
    decision = gate.assess(
        _request(
            action_type="propose_patch",
            target_type="repo_file",
            target_path_or_ref="src/example.py",
            requested_zone="sandbox",
            writes_state=True,
            requested_operation="propose_patch",
            target_scope="repo_local",
            mutation_depth="proposal_only",
            zone_preference="sandbox",
            why_not_host_if_applicable="sandbox keeps proposed or bounded transforms away from host mutation",
            reason="propose a bounded patch",
        )
    )

    assert decision.decision == "require_approval"
    assert decision.mutation_depth == "proposal_only"
    assert decision.recommended_zone == "sandbox"


def test_run_shell_with_unknown_trust_does_not_auto_allow() -> None:
    gate = ExecutionGate()
    decision = gate.assess(
        _request(
            action_type="execute_payload",
            target_type="script",
            target_path_or_ref="generated_script.py",
            requested_zone="host",
            executes_code=True,
            source_trust_stage="unknown",
            requested_operation="run_shell",
            target_scope="repo_local",
            mutation_depth="none",
            zone_preference="host",
            reason="run generated code",
        )
    )

    assert decision.decision != "allow"


def test_approval_object_defaults_to_false() -> None:
    approval = ApprovalRequest(
        requested_action="write_file:repo_file:src/example.py",
        why_needed="mutation requested",
        risk_summary="state mutation requires approval",
        sandbox_alternative_available=True,
        why_host_not_sandbox="host mutation is not least-privilege here",
    )

    assert approval.approved is False


def test_output_remains_compact_and_auditable() -> None:
    gate = ExecutionGate()
    exported = gate.export_decision(gate.assess(_request()))

    assert set(exported.keys()) == {
        "decision",
        "recommended_zone",
        "requires_approval",
        "risk_summary",
        "reason",
        "requested_operation",
        "target_scope",
        "target_trust",
        "mutation_depth",
    }


def test_no_sleep_logic_is_introduced() -> None:
    gate = ExecutionGate()
    exported = gate.export_decision(gate.assess(_request()))

    assert "sleep_state" not in exported
    assert "wake_state" not in exported


def test_no_actual_execution_side_effect_fields_are_introduced() -> None:
    gate = ExecutionGate()
    exported = gate.export_decision(
        gate.assess(
            _request(
                action_type="shell_execute",
                target_type="command",
                target_path_or_ref="echo hi",
                executes_code=True,
                source_trust_stage="unknown",
                requested_operation="run_shell",
                target_scope="repo_local",
                mutation_depth="none",
                zone_preference="host",
                reason="attempt execution",
            )
        )
    )

    assert "executed" not in exported
    assert "filesystem_mutation" not in exported
    assert "network_session" not in exported


def test_secret_access_is_not_auto_allowed() -> None:
    gate = ExecutionGate()
    decision = gate.assess(
        _request(
            action_type="secret_access",
            target_type="secret_ref",
            target_path_or_ref="OPENAI_API_KEY",
            requested_zone="host",
            secret_access_required=True,
            requested_operation="access_secret",
            target_scope="unknown",
            mutation_depth="none",
            zone_preference="host",
            reason="read a secret",
        )
    )

    assert decision.decision in {"require_approval", "deny"}


def test_external_untrusted_network_access_does_not_auto_allow() -> None:
    gate = ExecutionGate()
    decision = gate.assess(
        _request(
            action_type="network_access",
            target_type="remote_ref",
            target_path_or_ref="https://untrusted.example/api",
            requested_zone="host",
            network_required=True,
            source_trust_stage="untrusted",
            requested_operation="access_network",
            target_scope="external_destination",
            mutation_depth="none",
            zone_preference="host",
            reason="fetch remote content",
        )
    )

    assert decision.decision != "allow"
