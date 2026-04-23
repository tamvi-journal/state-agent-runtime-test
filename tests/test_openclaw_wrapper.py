from __future__ import annotations

import json
import subprocess

from integration.openclaw_wrapper import OpenClawWrapper
from integration.payload_contracts import CONTRACT_SCHEMA_VERSION


def completed_process(*, returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["python", "-m", "src.integration.openclaw_entrypoint"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_openclaw_wrapper_builds_minimal_payload() -> None:
    wrapper = OpenClawWrapper(python_executable="python")

    payload = wrapper.build_payload(
        request_id="req-wrap-1",
        request_text="Analyze MBB technically.",
        session={"session_id": "finance_mbb_daily"},
        host_metadata={"channel": "telegram"},
        kernel_options={"return_debug_trace": False},
    )

    assert payload["schema_version"] == CONTRACT_SCHEMA_VERSION
    assert payload["request_id"] == "req-wrap-1"
    assert payload["request_text"] == "Analyze MBB technically."
    assert payload["session"]["session_id"] == "finance_mbb_daily"


def test_openclaw_wrapper_invokes_entrypoint_once_via_subprocess(monkeypatch) -> None:
    wrapper = OpenClawWrapper(python_executable="python")
    calls: list[dict[str, object]] = []

    def fake_run(cmd, input, capture_output, text, cwd, check):  # type: ignore[no-untyped-def]
        calls.append(
            {
                "cmd": cmd,
                "input": input,
                "capture_output": capture_output,
                "text": text,
                "cwd": cwd,
                "check": check,
            }
        )
        return completed_process(
            stdout=json.dumps(
                {
                    "schema_version": CONTRACT_SCHEMA_VERSION,
                    "request_id": "req-wrap-2",
                    "status": "ok",
                    "final_response": "I checked MBB using market_data_worker.",
                    "baton": {"verification_status": "failed"},
                    "session_status_metadata": {
                        "current_status": "failed",
                        "primary_focus": "verify bounded market-data lookup for MBB",
                        "open_loops": ["verification remains open"],
                        "last_verified_outcomes": [],
                        "recent_decisions": ["inspect bounded evidence"],
                        "relevant_entities": [],
                        "active_skills": [],
                        "risk_notes": [],
                        "next_hint": "inspect bounded evidence",
                    },
                    "snapshot_candidates": [],
                    "verification_outcome": {
                        "status": "failed",
                        "observed_outcome": "ticker not found",
                        "record": {"verification_status": "failed"},
                    },
                    "worker_result": {"result": {"bars_found": 0}},
                }
            )
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    response = wrapper.invoke(
        request_id="req-wrap-2",
        request_text="Load MBB daily data",
        session={"session_id": "finance_mbb_daily"},
        host_metadata={"route": "state_agent_finance"},
    )

    assert len(calls) == 1
    assert calls[0]["cmd"] == ["python", "-m", "src.integration.openclaw_entrypoint"]
    assert response["status"] == "ok"
    assert response["verification_outcome"]["status"] == "failed"
    assert response["baton"]["verification_status"] == "failed"


def test_openclaw_wrapper_preserves_error_response_without_flattening(monkeypatch) -> None:
    wrapper = OpenClawWrapper(python_executable="python")

    def fake_run(cmd, input, capture_output, text, cwd, check):  # type: ignore[no-untyped-def]
        return completed_process(
            stdout=json.dumps(
                {
                    "schema_version": CONTRACT_SCHEMA_VERSION,
                    "request_id": "req-wrap-3",
                    "status": "error",
                    "error": {
                        "error_type": "invalid_payload",
                        "message": "bad request",
                        "retryable": False,
                    },
                }
            )
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    response = wrapper.invoke(
        request_id="req-wrap-3",
        request_text="bad request",
    )

    assert response["status"] == "error"
    assert response["error"]["error_type"] == "invalid_payload"


def test_openclaw_wrapper_raises_on_process_failure(monkeypatch) -> None:
    wrapper = OpenClawWrapper(python_executable="python")

    def fake_run(cmd, input, capture_output, text, cwd, check):  # type: ignore[no-untyped-def]
        return completed_process(returncode=2, stderr="process failed")

    monkeypatch.setattr(subprocess, "run", fake_run)

    try:
        wrapper.invoke(
            request_id="req-wrap-4",
            request_text="Load MBB daily data",
        )
    except RuntimeError as exc:
        assert "exit code 2" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")
