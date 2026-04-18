from __future__ import annotations

from pathlib import Path

from tools.market_data_tool import MarketDataTool


def write_csv(path: Path) -> None:
    path.write_text(
        "date,ticker,open,high,low,close,volume\n"
        "2026-04-08,MBB,24.6,24.9,24.4,24.8,14500000\n"
        "2026-04-09,MBB,24.8,25.0,24.7,24.9,16200000\n"
        "2026-04-10,MBB,24.8,25.2,24.6,25.1,18450200\n",
        encoding="utf-8",
    )


def test_market_data_tool_loads_and_normalizes_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    tool = MarketDataTool(data_path=csv_path)
    result = tool.load_market_data(ticker="MBB", timeframe="1D")

    assert result.tool_name == "market_data_tool"
    assert result.status == "ok"
    assert result.data["bars_found"] == 3
    assert result.data["latest_bar"]["close"] == 25.1
    assert len(result.data["recent_rows"]) == 3
    assert result.data["integrity_checks"]["price_order_valid"] is True


def test_market_data_tool_reports_missing_file(tmp_path: Path) -> None:
    csv_path = tmp_path / "missing.csv"

    tool = MarketDataTool(data_path=csv_path)
    result = tool.load_market_data(ticker="MBB", timeframe="1D")

    assert result.status == "not_found"
    assert result.data["bars_found"] == 0
    assert result.data["integrity_checks"]["file_exists"] is False
