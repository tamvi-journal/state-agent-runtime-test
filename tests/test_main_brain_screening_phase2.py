from __future__ import annotations

from core.main_brain import MainBrain
from state.live_state import LiveState
from state.state_manager import StateManager
from verification.verification_record import VerificationRecord


def build_main_brain() -> MainBrain:
    live_state = LiveState(
        active_mode="build",
        current_axis="technical",
        coherence_level=0.92,
        tension_flags=[],
        active_project="state-memory-agent",
        user_signal="phase 2 screening test",
        continuity_anchor="pytest-screening",
        archive_needed=False,
    )
    return MainBrain(state_manager=StateManager(live_state=live_state))


def sample_screening_payload() -> dict:
    return {
        "worker_name": "screening_worker",
        "result": {
            "screen_name": "close_volume_basic_v1",
            "universe_size": 3,
            "passed_count": 2,
            "filters_applied": [
                "close_gte_min_close",
                "avg_volume_gte_min_avg_volume",
            ],
            "candidates": [
                {
                    "ticker": "VCI",
                    "rank": 1,
                    "reason_codes": [
                        "close_gte_min_close",
                        "avg_volume_gte_min_avg_volume",
                    ],
                    "metrics": {
                        "close": 41.3,
                        "avg_volume_3": 8947366,
                        "bars_available": 3,
                    },
                    "score": 50.2474,
                },
                {
                    "ticker": "MBB",
                    "rank": 2,
                    "reason_codes": [
                        "close_gte_min_close",
                        "avg_volume_gte_min_avg_volume",
                    ],
                    "metrics": {
                        "close": 25.1,
                        "avg_volume_3": 16383400,
                        "bars_available": 3,
                    },
                    "score": 41.4834,
                },
            ],
            "data_source": "tmp/screening_data.csv",
            "integrity_checks": {
                "file_exists": True,
                "required_columns_present": True,
            },
        },
        "confidence": 0.88,
        "assumptions": [],
        "warnings": [],
        "trace": ["screened candidates and returned ranked subset"],
        "proposed_memory_update": None,
    }


def sample_record(status: str, observed: str) -> VerificationRecord:
    return VerificationRecord(
        intended_action="run screening_worker",
        executed_action="screening_worker.run(...)",
        expected_change="bounded screening payload should exist",
        observed_outcome=observed,
        verification_status=status,
    )


def test_main_brain_builder_render_screening_payload() -> None:
    main_brain = build_main_brain()
    response = main_brain.synthesize_worker_result(
        interpreted={"ticker": "", "worker_name": "screening_worker", "task_type": "screening"},
        worker_payload=sample_screening_payload(),
        verification_record=sample_record("passed", "worker returned 2 ranked candidates"),
        render_mode="builder",
    )

    assert "Main brain used screening_worker" in response
    assert "Worker confidence: 0.88" in response
    assert "Verification status: passed" in response


def test_main_brain_user_render_screening_payload() -> None:
    main_brain = build_main_brain()
    response = main_brain.synthesize_worker_result(
        interpreted={"ticker": "", "worker_name": "screening_worker", "task_type": "screening"},
        worker_payload=sample_screening_payload(),
        verification_record=sample_record("passed", "worker returned 2 ranked candidates"),
        render_mode="user",
    )

    assert "screening_worker" in response
    assert "Verification passed." in response
