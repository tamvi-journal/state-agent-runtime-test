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


def test_shell_execute_on_host_requires_approval_or_denial() -> None:
    gate = ExecutionGate()
    decision = gate.assess(
        _request(
            action_type="shell_execute",
            target_type="command",
            target_path_or_ref="python -m pytest",
            requested_zone="host",
            executes_code=True,
            source_trust_stage="reviewed",
            reason="run host command",
        )
    )

    assert decision.decision in {"require_approval", "deny"}
    assert decision.recommended_zone in {"sandbox", "host"}


def test_package_install_is_not_auto_allowed() -> None:
    gate = ExecutionGate()
    decision = gate.assess(
        _request(
            action_type="install",
            target_type="package",
            target_path_or_ref="pytest",
            requested_zone="host",
            package_install_required=True,
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
            reason="write a repository file",
        )
    )

    assert decision.decision == "require_approval"
    assert decision.requires_approval is True


def test_unknown_trust_executable_content_does_not_auto_allow() -> None:
    gate = ExecutionGate()
    decision = gate.assess(
        _request(
            action_type="execute_payload",
            target_type="script",
            target_path_or_ref="generated_script.py",
            requested_zone="sandbox",
            executes_code=True,
            source_trust_stage="unknown",
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
                reason="attempt execution",
            )
        )
    )

    assert "executed" not in exported
    assert "filesystem_mutation" not in exported
    assert "network_session" not in exported
