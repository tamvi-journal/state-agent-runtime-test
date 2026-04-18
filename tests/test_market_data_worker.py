from __future__ import annotations

from pathlib import Path

from tools.market_data_tool import MarketDataTool
from workers.market_data_worker import MarketDataWorker


def write_csv(path: Path) -> None:
    path.write_text(
        "date,ticker,open,high,low,close,volume\n"
        "2026-04-08,MBB,24.6,24.9,24.4,24.8,14500000\n"
        "2026-04-09,MBB,24.8,25.0,24.7,24.9,16200000\n"
        "2026-04-10,MBB,24.8,25.2,24.6,25.1,18450200\n",
        encoding="utf-8",
    )


def test_market_data_worker_returns_payload_for_existing_ticker(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    worker = MarketDataWorker(market_data_tool=MarketDataTool(data_path=csv_path))
    payload = worker.run(ticker="MBB", timeframe="1D")

    assert payload["worker_name"] == "market_data_worker"
    assert payload["confidence"] > 0.0
    assert payload["result"]["ticker"] == "MBB"
    assert payload["result"]["bars_found"] == 3
    assert payload["result"]["latest_bar"]["close"] == 25.1
    trace = " ".join(payload["trace"])
    assert "delegating bounded execution to market_data_tool.load_market_data" in trace
    assert "normalized 3 rows into bounded OHLCV records" in trace
    assert payload["assumptions"][0] == "tool owns raw csv read, parse, normalize, and integrity-check work"


def test_market_data_worker_handles_missing_file(tmp_path: Path) -> None:
    csv_path = tmp_path / "missing.csv"

    worker = MarketDataWorker(market_data_tool=MarketDataTool(data_path=csv_path))
    payload = worker.run(ticker="MBB", timeframe="1D")

    assert payload["worker_name"] == "market_data_worker"
    assert payload["confidence"] == 0.0
    assert payload["result"]["bars_found"] == 0
    assert payload["result"]["integrity_checks"]["file_exists"] is False


def test_market_data_worker_handles_missing_ticker(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    worker = MarketDataWorker(market_data_tool=MarketDataTool(data_path=csv_path))
    payload = worker.run(ticker="VCB", timeframe="1D")

    assert payload["result"]["ticker"] == "VCB"
    assert payload["result"]["bars_found"] == 0
    assert payload["result"]["integrity_checks"]["ticker_match_found"] is False
