from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import csv

from tools.contracts import ToolRequest, ToolResult

RECENT_ROWS_LIMIT = 30


@dataclass(slots=True)
class MarketDataTool:
    data_path: str | Path

    def __post_init__(self) -> None:
        self.data_path = str(self.data_path)

    def load_market_data(self, *, ticker: str, timeframe: str = "1D") -> ToolResult:
        normalized_ticker = ticker.strip().upper()
        path = Path(self.data_path)
        request = ToolRequest(
            tool_name="market_data_tool",
            action_name="load_market_data",
            target=str(path),
            arguments={"ticker": normalized_ticker, "timeframe": timeframe},
        )
        trace = [
            f"tool request accepted for ticker={normalized_ticker} timeframe={timeframe}",
            f"reading bounded csv source at {path}",
        ]

        if not path.exists():
            return ToolResult(
                tool_name=request.tool_name,
                action_name=request.action_name,
                target=request.target,
                status="not_found",
                data={
                    "ticker": normalized_ticker,
                    "timeframe": timeframe,
                    "bars_found": 0,
                    "recent_rows": [],
                    "data_source": str(path),
                    "integrity_checks": {
                        "file_exists": False,
                        "required_columns_present": False,
                    },
                },
                trace=trace + ["data file missing"],
                warnings=["data file does not exist"],
                error="data file does not exist",
            )

        rows = self._load_csv_rows(path)
        trace.append(f"parsed {len(rows)} raw rows from csv")
        required_columns = ["date", "ticker", "open", "high", "low", "close", "volume"]

        if not rows:
            return ToolResult(
                tool_name=request.tool_name,
                action_name=request.action_name,
                target=request.target,
                status="empty",
                data={
                    "ticker": normalized_ticker,
                    "timeframe": timeframe,
                    "bars_found": 0,
                    "recent_rows": [],
                    "data_source": str(path),
                    "integrity_checks": {
                        "file_exists": True,
                        "required_columns_present": False,
                    },
                },
                trace=trace + ["csv was empty"],
                warnings=["csv file is empty"],
                error="csv file is empty",
            )

        missing_columns = [col for col in required_columns if col not in rows[0]]
        if missing_columns:
            return ToolResult(
                tool_name=request.tool_name,
                action_name=request.action_name,
                target=request.target,
                status="invalid",
                data={
                    "ticker": normalized_ticker,
                    "timeframe": timeframe,
                    "bars_found": 0,
                    "recent_rows": [],
                    "data_source": str(path),
                    "integrity_checks": {
                        "file_exists": True,
                        "required_columns_present": False,
                        "missing_columns": missing_columns,
                    },
                },
                trace=trace + ["required column check failed"],
                warnings=[f"missing required columns: {missing_columns}"],
                error="missing required columns",
            )

        filtered = self._filter_rows_for_ticker(rows=rows, ticker=normalized_ticker)
        trace.append(f"filtered to {len(filtered)} rows for ticker={normalized_ticker}")

        if not filtered:
            return ToolResult(
                tool_name=request.tool_name,
                action_name=request.action_name,
                target=request.target,
                status="ok",
                data={
                    "ticker": normalized_ticker,
                    "timeframe": timeframe,
                    "bars_found": 0,
                    "recent_rows": [],
                    "data_source": str(path),
                    "integrity_checks": {
                        "file_exists": True,
                        "required_columns_present": True,
                        "ticker_match_found": False,
                    },
                },
                trace=trace + ["ticker filter returned no rows"],
                warnings=[f"ticker {normalized_ticker} not found in csv"],
            )

        normalized_rows = [self._normalize_row(row) for row in filtered]
        recent_rows = normalized_rows[-RECENT_ROWS_LIMIT:]
        trace.append(f"normalized {len(normalized_rows)} rows into bounded OHLCV records")
        integrity_checks = self._integrity_checks(normalized_rows)

        warnings: list[str] = []
        if not integrity_checks["price_order_valid"]:
            warnings.append("latest or historical price ordering failed basic OHLC check")
        if integrity_checks["duplicate_dates_detected"]:
            warnings.append("duplicate dates detected for ticker")
        if integrity_checks["volume_null_detected"]:
            warnings.append("one or more volume values could not be parsed")
        if integrity_checks["missing_dates_detected"]:
            warnings.append("date ordering suggests missing or unsorted bars")

        return ToolResult(
            tool_name=request.tool_name,
            action_name=request.action_name,
            target=request.target,
            status="ok",
            data={
                "ticker": normalized_ticker,
                "timeframe": timeframe,
                "bars_found": len(normalized_rows),
                "recent_rows": recent_rows,
                "date_range": {
                    "start": normalized_rows[0]["date"],
                    "end": normalized_rows[-1]["date"],
                },
                "latest_bar": normalized_rows[-1],
                "data_source": str(path),
                "integrity_checks": integrity_checks,
            },
            trace=trace + ["calculated integrity checks for normalized rows"],
            warnings=warnings,
        )

    def _load_csv_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as file_handle:
            reader = csv.DictReader(file_handle)
            return [dict(row) for row in reader]

    @staticmethod
    def _filter_rows_for_ticker(*, rows: list[dict[str, str]], ticker: str) -> list[dict[str, str]]:
        return [row for row in rows if str(row.get("ticker", "")).upper() == ticker]

    def _normalize_row(self, row: dict[str, str]) -> dict[str, Any]:
        return {
            "date": str(row.get("date", "")),
            "open": self._to_float(row.get("open")),
            "high": self._to_float(row.get("high")),
            "low": self._to_float(row.get("low")),
            "close": self._to_float(row.get("close")),
            "volume": self._to_int(row.get("volume")),
        }

    def _integrity_checks(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        duplicate_dates_detected = len({row["date"] for row in rows}) != len(rows)
        volume_null_detected = any(row["volume"] is None for row in rows)

        price_order_valid = True
        for row in rows:
            open_price = row["open"]
            high_price = row["high"]
            low_price = row["low"]
            close_price = row["close"]
            numeric_values = [value for value in [open_price, high_price, low_price, close_price] if value is not None]
            if len(numeric_values) != 4:
                price_order_valid = False
                break
            if not (low_price <= open_price <= high_price and low_price <= close_price <= high_price):
                price_order_valid = False
                break

        dates = [row["date"] for row in rows]
        missing_dates_detected = dates != sorted(dates)

        return {
            "file_exists": True,
            "required_columns_present": True,
            "ticker_match_found": True,
            "missing_dates_detected": missing_dates_detected,
            "duplicate_dates_detected": duplicate_dates_detected,
            "volume_null_detected": volume_null_detected,
            "price_order_valid": price_order_valid,
        }

    @staticmethod
    def _to_float(value: Any) -> float | None:
        try:
            if value is None or str(value).strip() == "":
                return None
            return float(str(value).replace(",", ""))
        except ValueError:
            return None

    @staticmethod
    def _to_int(value: Any) -> int | None:
        try:
            if value is None or str(value).strip() == "":
                return None
            return int(float(str(value).replace(",", "")))
        except ValueError:
            return None
