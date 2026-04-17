from __future__ import annotations

from family.execution_gate import ExecutionGate
from family.execution_types import ExecutionRequest


def run() -> None:
    gate = ExecutionGate()

    safe = gate.assess(
        ExecutionRequest(
            action_type="inspect",
            target_type="repo_metadata",
            target_path_or_ref="README.md",
            requested_zone="inspection",
            source_trust_stage="reviewed",
            reason="read metadata only",
        )
    )
    assert safe.decision == "allow"
    assert safe.recommended_zone == "inspection"

    approval = gate.assess(
        ExecutionRequest(
            action_type="write_file",
            target_type="repo_file",
            target_path_or_ref="src/family/example.py",
            requested_zone="host",
            writes_state=True,
            source_trust_stage="reviewed",
            reason="proposed repository mutation",
        )
    )
    assert approval.decision == "require_approval"

    deny = gate.assess(
        ExecutionRequest(
            action_type="install",
            target_type="package",
            target_path_or_ref="pytest",
            requested_zone="host",
            package_install_required=True,
            source_trust_stage="unknown",
            reason="dependency install",
        )
    )
    assert deny.decision == "deny"

    sandbox = gate.assess(
        ExecutionRequest(
            action_type="inspect",
            target_type="structured_payload",
            target_path_or_ref="generated_output.json",
            requested_zone="sandbox",
            source_trust_stage="unknown",
            reason="controlled parsing of generated payload",
        )
    )
    assert sandbox.recommended_zone == "sandbox"

    print("execution_gate_smoke: ok")


if __name__ == "__main__":
    run()
