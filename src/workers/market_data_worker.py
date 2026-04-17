from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import csv

from workers.contracts import WorkerContractValidator


@dataclass(slots=True)
class MarketDataWorker:
    """
    First bounded worker.

    Responsibilities:
    - load normalized OHLCV-like data from a local CSV
    - filter by ticker
    - run basic integrity checks
    - return a strict worker contract payload

    Non-goals:
    - no trading advice
    - no ranking
    - no interpretation beyond data integrity
    """

    data_path: str | Path
    validator: WorkerContractValidator | None = None

    def __post_init__(self) -> None:
        self.data_path = str(self.data_path)
        if self.validator is None:
            self.validator = WorkerContractValidator()

    def run(self, *, ticker: str, timeframe: str = "1D") -> dict[str, Any]:
        trace: list[str] = [
            f"received request for ticker={ticker} timeframe={timeframe}",
        ]
        assumptions: list[str] = [
            "input csv is intended to be normalized",
            "timeframe is informational unless explicitly encoded in file",
            "worker only validates local file content, not upstream truth",
        ]
        warnings: list[str] = []

        ticker = ticker.strip().upper()
        path = Path(self.data_path)

        if not path.exists():
            payload = {
                "worker_name": "market_data_worker",
                "result": {
                    "ticker": ticker,
                    "timeframe": timeframe,
                    "bars_found": 0,
                    "data_source": str(path),
                    "integrity_checks": {
                        "file_exists": False,
                        "required_columns_present": False,
                    },
                },
                "confidence": 0.0,
                "assumptions": assumptions,
                "warnings": ["data file does not exist"],
                "trace": trace + ["file missing"],
                "proposed_memory_update": None,
            }
            return self.validator.validate(payload)

        rows = self._load_csv_rows(path)
        trace.append(f"loaded {len(rows)} raw rows from csv")

        required_columns = ["date", "ticker", "open", "high", "low", "close", "volume"]
        if not rows:
            payload = {
                "worker_name": "market_data_worker",
                "result": {
                    "ticker": ticker,
                    "timeframe": timeframe,
                    "bars_found": 0,
                    "data_source": str(path),
                    "integrity_checks": {
                        "file_exists": True,
                        "required_columns_present": False,
                    },
                },
                "confidence": 0.2,
                "assumptions": assumptions,
                "warnings": ["csv file is empty"],
                "trace": trace + ["empty csv"],
                "proposed_memory_update": None,
            }
            return self.validator.validate(payload)

        missing_columns = [col for col in required_columns if col not in rows[0]]
        if missing_columns:
            payload = {
                "worker_name": "market_data_worker",
                "result": {
                    "ticker": ticker,
                    "timeframe": timeframe,
                    "bars_found": 0,
                    "data_source": str(path),
                    "integrity_checks": {
                        "file_exists": True,
                        "required_columns_present": False,
                        "missing_columns": missing_columns,
                    },
                },
                "confidence": 0.1,
                "assumptions": assumptions,
                "warnings": [f"missing required columns: {missing_columns}"],
                "trace": trace + ["required column check failed"],
                "proposed_memory_update": None,
            }
            return self.validator.validate(payload)

        filtered = [row for row in rows if str(row.get("ticker", "")).upper() == ticker]
        trace.append(f"filtered to {len(filtered)} rows for ticker={ticker}")

        if not filtered:
            payload = {
                "worker_name": "market_data_worker",
                "result": {
                    "ticker": ticker,
                    "timeframe": timeframe,
                    "bars_found": 0,
                    "data_source": str(path),
                    "integrity_checks": {
                        "file_exists": True,
                        "required_columns_present": True,
                        "ticker_match_found": False,
                    },
                },
                "confidence": 0.4,
                "assumptions": assumptions,
                "warnings": [f"ticker {ticker} not found in csv"],
                "trace": trace + ["ticker filter returned no rows"],
                "proposed_memory_update": None,
            }
            return self.validator.validate(payload)

        normalized_rows = [self._normalize_row(row) for row in filtered]
        latest_bar = normalized_rows[-1]

        integrity_checks = self._integrity_checks(normalized_rows)
        trace.append("ran integrity checks")
        if not integrity_checks["price_order_valid"]:
            warnings.append("latest or historical price ordering failed basic OHLC check")
        if integrity_checks["duplicate_dates_detected"]:
            warnings.append("duplicate dates detected for ticker")
        if integrity_checks["volume_null_detected"]:
            warnings.append("one or more volume values could not be parsed")
        if integrity_checks["missing_dates_detected"]:
            warnings.append("date ordering suggests missing or unsorted bars")

        confidence = 0.96
        if warnings:
            confidence = 0.75

        payload = {
            "worker_name": "market_data_worker",
            "result": {
                "ticker": ticker,
                "timeframe": timeframe,
                "bars_found": len(normalized_rows),
                "date_range": {
                    "start": normalized_rows[0]["date"],
                    "end": normalized_rows[-1]["date"],
                },
                "latest_bar": latest_bar,
                "data_source": str(path),
                "integrity_checks": integrity_checks,
            },
            "confidence": confidence,
            "assumptions": assumptions,
            "warnings": warnings,
            "trace": trace + ["returned normalized market snapshot"],
            "proposed_memory_update": None,
        }
        return self.validator.validate(payload)

    def _load_csv_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]

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
        duplicate_dates_detected = len({r["date"] for r in rows}) != len(rows)
        volume_null_detected = any(r["volume"] is None for r in rows)

        price_order_valid = True
        for r in rows:
            o, h, l, c = r["open"], r["high"], r["low"], r["close"]
            numeric_values = [v for v in [o, h, l, c] if v is not None]
            if len(numeric_values) != 4:
                price_order_valid = False
                break
            if not (l <= o <= h and l <= c <= h):
                price_order_valid = False
                break

        dates = [r["date"] for r in rows]
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