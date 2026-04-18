from __future__ import annotations

from pathlib import Path

from tools.market_data_tool import MarketDataTool
from workers.technical_analysis_worker import TechnicalAnalysisWorker


def write_csv(path: Path) -> None:
    path.write_text(
        "date,ticker,open,high,low,close,volume\n"
        "2026-04-07,MBB,24.2,24.5,24.0,24.3,11000000\n"
        "2026-04-08,MBB,24.4,24.9,24.3,24.8,14500000\n"
        "2026-04-09,MBB,24.8,25.0,24.7,24.9,16200000\n"
        "2026-04-10,MBB,24.8,25.2,24.6,25.1,18450200\n"
        "2026-04-11,MBB,25.1,25.4,25.0,25.3,19500000\n",
        encoding="utf-8",
    )


def test_technical_analysis_worker_returns_structured_evidence(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    worker = TechnicalAnalysisWorker(market_data_tool=MarketDataTool(data_path=csv_path))
    payload = worker.run(ticker="MBB", timeframe="1D")

    assert payload["worker_name"] == "technical_analysis_worker"
    assert payload["result"]["symbol"] == "MBB"
    assert payload["result"]["data_status"] in {"loaded", "partial"}
    assert payload["result"]["alignment_status"] in {"bullish", "bearish", "mixed", "range", "unresolved"}
    assert isinstance(payload["result"]["indicator_read"], dict)
    assert "moving_averages" in payload["result"]["indicator_read"]
    assert payload["result"]["bars_found"] == 5
    assert payload["confidence"] > 0.0


def test_technical_analysis_worker_preserves_weak_data_honesty(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    csv_path.write_text(
        "date,ticker,open,high,low,close,volume\n"
        "2026-04-10,MBB,24.8,25.2,24.6,25.1,18450200\n"
        "2026-04-11,MBB,25.1,25.4,25.0,25.3,19500000\n",
        encoding="utf-8",
    )

    worker = TechnicalAnalysisWorker(market_data_tool=MarketDataTool(data_path=csv_path))
    payload = worker.run(ticker="MBB", timeframe="1D")

    assert payload["result"]["data_status"] == "partial"
    assert payload["confidence"] < 0.6
    assert any("partial" in warning for warning in payload["warnings"])
