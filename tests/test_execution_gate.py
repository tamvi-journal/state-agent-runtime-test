from __future__ import annotations

from pathlib import Path

from observability.logger import EventLogger
from observability.trace_events import TraceEvents
from runtime.execution_gate import ExecutionGate
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


def test_execution_gate_returns_passed_record_when_worker_finds_data(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    logger = EventLogger()
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(data_path=csv_path),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=logger),
    )

    payload, record = gate.run_market_data_flow(ticker="MBB", timeframe="1D")

    assert payload["result"]["bars_found"] == 3
    assert record.verification_status == "passed"
    categories = [event["category"] for event in logger.all_events()]
    assert "worker_trace" in categories
    assert "verification_event" in categories


def test_execution_gate_returns_failed_record_when_worker_finds_no_data(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    logger = EventLogger()
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(data_path=csv_path),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=logger),
    )

    payload, record = gate.run_market_data_flow(ticker="VCB", timeframe="1D")

    assert payload["result"]["bars_found"] == 0
    assert record.verification_status == "failed"
