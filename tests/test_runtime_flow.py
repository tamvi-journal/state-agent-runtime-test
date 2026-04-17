from __future__ import annotations

from pathlib import Path

from core.main_brain import MainBrain
from observability.logger import EventLogger
from observability.trace_events import TraceEvents
from runtime.execution_gate import ExecutionGate
from runtime.request_router import RequestRouter
from state.live_state import LiveState
from state.state_manager import StateManager
from verification.verification_loop import VerificationLoop
from workers.market_data_worker import MarketDataWorker


def write_csv(path: Path) -> None:
    path.write_text(
        "date,ticker,open,high,low,close,volume\n"
        "2026-04-08,MBB,24.6,24.9,24.4,24.8,14500000\n"
        "2026-04-09,MBB,24.8,25.0,24.7,24.9,16200000\n"
        "2026-04-10,MBB,24.8,25.2,24.6,25.1,18450200\n",
        encoding="utf-8",
    )


def build_main_brain() -> MainBrain:
    live_state = LiveState(
        active_mode="build",
        current_axis="technical",
        coherence_level=0.92,
        tension_flags=[],
        active_project="state-memory-agent",
        user_signal="test runtime flow",
        continuity_anchor="pytest-flow",
        archive_needed=False,
    )
    return MainBrain(state_manager=StateManager(live_state=live_state))


def test_runtime_flow_happy_path(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    main_brain = build_main_brain()
    router = RequestRouter(main_brain=main_brain)

    logger = EventLogger()
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(data_path=csv_path),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=logger),
    )

    interpreted = main_brain.interpret_request("Load MBB daily data")
    assert interpreted["needs_worker"] is True
    assert interpreted["ticker"] == "MBB"

    payload, verification_record = gate.run_market_data_flow(ticker="MBB", timeframe="1D")
    final_response = router.route(
        "Load MBB daily data",
        worker_payload=payload,
        verification_record=verification_record,
    )

    assert "I checked MBB using market_data_worker." in final_response
    assert "Verification passed." in final_response
    assert "Latest daily bar:" in final_response


def test_runtime_flow_failure_path(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    main_brain = build_main_brain()
    router = RequestRouter(main_brain=main_brain)

    logger = EventLogger()
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(data_path=csv_path),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=logger),
    )

    payload, verification_record = gate.run_market_data_flow(ticker="VCB", timeframe="1D")
    final_response = router.route(
        "Load VCB daily data",
        worker_payload=payload,
        verification_record=verification_record,
    )

    assert "Verification failed." in final_response
    assert "No bars were returned for this ticker in the current dataset." in final_response