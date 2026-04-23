from __future__ import annotations

import json
import subprocess
from pathlib import Path

from integration.openclaw_wrapper import OpenClawWrapper
from integration.payload_contracts import CONTRACT_SCHEMA_VERSION
from integration.session_roundtrip_store import SessionRoundtripStore


def completed_process(*, returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["python", "-m", "src.integration.openclaw_entrypoint"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def ok_response(*, request_id: str, verification_status: str = "passed") -> str:
    return json.dumps(
        {
            "schema_version": CONTRACT_SCHEMA_VERSION,
            "request_id": request_id,
            "status": "ok",
            "final_response": "bounded response",
            "baton": {
                "task_focus": "verify bounded market-data lookup for MBB",
                "active_mode": "build",
                "open_loops": ["verification remains open"],
                "verification_status": verification_status,
                "next_hint": "inspect bounded evidence",
            },
            "session_status_metadata": {
                "current_status": verification_status,
                "primary_focus": "verify bounded market-data lookup for MBB",
                "open_loops": ["verification remains open"],
                "last_verified_outcomes": ["prior read classified as mixed"] if verification_status == "passed" else [],
                "recent_decisions": ["inspect bounded evidence"],
                "relevant_entities": ["MBB"],
                "active_skills": ["technical_analysis"],
                "risk_notes": [],
                "next_hint": "inspect bounded evidence",
            },
            "snapshot_candidates": [
                {
                    "candidate_type": "handoff_baton",
                    "task_focus": "verify bounded market-data lookup for MBB",
                    "verification_status": verification_status,
                    "next_hint": "inspect bounded evidence",
                    "tracey_turn": {"should_not_persist": True},
                }
            ],
            "verification_outcome": {
                "status": verification_status,
                "observed_outcome": "prior read classified as mixed",
                "record": {"verification_status": verification_status},
            },
            "worker_result": {"result": {"bars_found": 3}},
        }
    )


def test_session_roundtrip_first_write_creates_compact_snapshot(monkeypatch, tmp_path: Path) -> None:
    wrapper = OpenClawWrapper(python_executable="python")
    store_dir = tmp_path / "session_roundtrip"

    def fake_run(cmd, input, capture_output, text, cwd, check):  # type: ignore[no-untyped-def]
        return completed_process(stdout=ok_response(request_id="req-roundtrip-1"))

    monkeypatch.setattr(subprocess, "run", fake_run)
    response = wrapper.invoke(
        request_id="req-roundtrip-1",
        request_text="Analyze MBB technically.",
        session_id="finance/mbb:daily",
        persist_roundtrip=True,
        store_dir=str(store_dir),
    )

    assert response["status"] == "ok"
    stored_path = store_dir / "finance_mbb_daily.json"
    assert stored_path.exists()
    stored = json.loads(stored_path.read_text(encoding="utf-8"))
    assert stored["session"]["session_id"] == "finance/mbb:daily"
    assert "tracey_turn" not in stored
    assert "gate_decision" not in stored
    assert "monitor_summary" not in stored
    assert stored["snapshot_candidates"][0]["candidate_type"] == "handoff_baton"
    assert "tracey_turn" not in stored["snapshot_candidates"][0]


def test_session_roundtrip_loads_and_reuses_stored_session(monkeypatch, tmp_path: Path) -> None:
    wrapper = OpenClawWrapper(python_executable="python")
    store_dir = tmp_path / "session_roundtrip"
    store = SessionRoundtripStore(root_dir=store_dir)
    store.save_snapshot(
        session_id="finance_mbb_daily",
        session_metadata={
            "session_id": "finance_mbb_daily",
            "session_kind": "analysis",
            "primary_focus": "MBB daily technical analysis",
            "current_status": "paused",
            "open_loops": ["check whether mixed signal resolved"],
            "last_verified_outcomes": ["prior read classified as mixed"],
            "recent_decisions": ["resume from mixed alignment"],
            "relevant_entities": ["MBB"],
            "active_skills": ["technical_analysis"],
            "risk_notes": ["mixed alignment"],
            "next_hint": "resume from mixed alignment",
        },
        baton={"verification_status": "failed"},
        snapshot_candidates=[],
    )

    calls: list[dict[str, object]] = []

    def fake_run(cmd, input, capture_output, text, cwd, check):  # type: ignore[no-untyped-def]
        calls.append(json.loads(input))
        return completed_process(stdout=ok_response(request_id="req-roundtrip-2"))

    monkeypatch.setattr(subprocess, "run", fake_run)
    wrapper.invoke(
        request_id="req-roundtrip-2",
        request_text="Continue from the previous chart read.",
        session_id="finance_mbb_daily",
        persist_roundtrip=True,
        store_dir=str(store_dir),
        session={"current_status": "resuming"},
    )

    assert len(calls) == 1
    sent_session = calls[0]["session"]
    assert sent_session["session_id"] == "finance_mbb_daily"
    assert sent_session["primary_focus"] == "MBB daily technical analysis"
    assert sent_session["current_status"] == "resuming"
    assert sent_session["next_hint"] == "resume from mixed alignment"


def test_session_roundtrip_status_error_does_not_overwrite(monkeypatch, tmp_path: Path) -> None:
    wrapper = OpenClawWrapper(python_executable="python")
    store_dir = tmp_path / "session_roundtrip"
    store = SessionRoundtripStore(root_dir=store_dir)
    original = store.save_snapshot(
        session_id="finance_mbb_daily",
        session_metadata={
            "session_id": "finance_mbb_daily",
            "session_kind": "analysis",
            "primary_focus": "MBB daily technical analysis",
            "current_status": "paused",
            "open_loops": [],
            "last_verified_outcomes": [],
            "recent_decisions": [],
            "relevant_entities": [],
            "active_skills": [],
            "risk_notes": [],
            "next_hint": "resume",
        },
        baton={"verification_status": "passed"},
        snapshot_candidates=[],
    )

    def fake_run(cmd, input, capture_output, text, cwd, check):  # type: ignore[no-untyped-def]
        return completed_process(
            stdout=json.dumps(
                {
                    "schema_version": CONTRACT_SCHEMA_VERSION,
                    "request_id": "req-roundtrip-3",
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
        request_id="req-roundtrip-3",
        request_text="bad request",
        session_id="finance_mbb_daily",
        persist_roundtrip=True,
        store_dir=str(store_dir),
    )

    assert response["status"] == "error"
    loaded = store.load_snapshot("finance_mbb_daily")
    assert loaded == original


def test_session_roundtrip_ok_with_failed_verification_still_persists(monkeypatch, tmp_path: Path) -> None:
    wrapper = OpenClawWrapper(python_executable="python")
    store_dir = tmp_path / "session_roundtrip"

    def fake_run(cmd, input, capture_output, text, cwd, check):  # type: ignore[no-untyped-def]
        return completed_process(stdout=ok_response(request_id="req-roundtrip-4", verification_status="failed"))

    monkeypatch.setattr(subprocess, "run", fake_run)
    response = wrapper.invoke(
        request_id="req-roundtrip-4",
        request_text="Analyze MBB technically.",
        session_id="finance_mbb_daily",
        persist_roundtrip=True,
        store_dir=str(store_dir),
    )

    assert response["status"] == "ok"
    assert response["verification_outcome"]["status"] == "failed"
    stored = SessionRoundtripStore(root_dir=store_dir).load_snapshot("finance_mbb_daily")
    assert stored is not None
    assert stored["session"]["current_status"] == "failed"
    assert stored["baton"]["verification_status"] == "failed"
