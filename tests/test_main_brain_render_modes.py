from __future__ import annotations

from brain.main_brain import MainBrain
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
        user_signal="test render modes",
        continuity_anchor="pytest-render",
        archive_needed=False,
    )
    return MainBrain(state_manager=StateManager(live_state=live_state))


def sample_payload() -> dict:
    return {
        "worker_name": "market_data_worker",
        "result": {
            "ticker": "MBB",
            "timeframe": "1D",
            "bars_found": 3,
            "date_range": {
                "start": "2026-04-08",
                "end": "2026-04-10",
            },
            "latest_bar": {
                "date": "2026-04-10",
                "open": 24.8,
                "high": 25.2,
                "low": 24.6,
                "close": 25.1,
                "volume": 18450200,
            },
            "data_source": "tmp/sample_market_data.csv",
            "integrity_checks": {
                "file_exists": True,
                "required_columns_present": True,
                "ticker_match_found": True,
                "missing_dates_detected": False,
                "duplicate_dates_detected": False,
                "volume_null_detected": False,
                "price_order_valid": True,
            },
        },
        "confidence": 0.96,
        "assumptions": [],
        "warnings": [],
        "trace": ["received request", "returned normalized market snapshot"],
        "proposed_memory_update": None,
    }


def sample_failed_payload() -> dict:
    return {
        "worker_name": "market_data_worker",
        "result": {
            "ticker": "VCB",
            "timeframe": "1D",
            "bars_found": 0,
            "data_source": "tmp/sample_market_data.csv",
            "integrity_checks": {
                "file_exists": True,
                "required_columns_present": True,
                "ticker_match_found": False,
            },
        },
        "confidence": 0.40,
        "assumptions": [],
        "warnings": ["ticker VCB not found in csv"],
        "trace": ["received request", "ticker filter returned no rows"],
        "proposed_memory_update": None,
    }


def sample_record(status: str, observed: str) -> VerificationRecord:
    return VerificationRecord(
        intended_action="run market_data_worker",
        executed_action="market_data_worker.run(...)",
        expected_change="bounded market-data payload should exist",
        observed_outcome=observed,
        verification_status=status,
    )


def test_main_brain_builder_render_passed() -> None:
    main_brain = build_main_brain()
    response = main_brain.handle_request(
        "Load MBB daily data",
        worker_payload=sample_payload(),
        verification_record=sample_record("passed", "worker returned bars_found=3 for ticker=MBB"),
        render_mode="builder",
    )

    assert "Main brain used market_data_worker for ticker MBB." in response
    assert "Worker confidence: 0.96" in response
    assert "Bars found: 3" in response
    assert "Integrity checks:" in response
    assert "Verification status: passed" in response


def test_main_brain_builder_render_failed() -> None:
    main_brain = build_main_brain()
    response = main_brain.handle_request(
        "Load VCB daily data",
        worker_payload=sample_failed_payload(),
        verification_record=sample_record("failed", "worker returned bars_found=0 for ticker=VCB"),
        render_mode="builder",
    )

    assert "Main brain used market_data_worker for ticker VCB." in response
    assert "Bars found: 0" in response
    assert "Verification status: failed" in response
    assert "Warnings:" in response
