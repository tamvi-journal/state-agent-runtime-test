from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import csv

from workers.contracts import WorkerContractValidator


@dataclass(slots=True)
class ScreeningWorker:
    """
    Second bounded worker.

    Responsibilities:
    - load normalized OHLCV-like data from a local CSV
    - apply simple mechanical screening rules
    - rank candidates using transparent scoring
    - return a strict worker contract payload

    Non-goals:
    - no buy/sell advice
    - no portfolio construction
    - no final judgment
    """

    data_path: str | Path
    validator: WorkerContractValidator | None = None

    def __post_init__(self) -> None:
        self.data_path = str(self.data_path)
        if self.validator is None:
            self.validator = WorkerContractValidator()

    def run(
        self,
        *,
        screen_name: str = "close_volume_basic_v1",
        min_close: float = 1.0,
        min_avg_volume: int = 0,
        top_n: int = 5,
    ) -> dict[str, Any]:
        trace: list[str] = [
            f"received screening request screen_name={screen_name} min_close={min_close} "
            f"min_avg_volume={min_avg_volume} top_n={top_n}",
        ]
        assumptions: list[str] = [
            "input csv is intended to be normalized",
            "screening is mechanical and bounded",
            "worker does not interpret final investment significance",
        ]
        warnings: list[str] = []

        path = Path(self.data_path)

        if not path.exists():
            payload = {
                "worker_name": "screening_worker",
                "result": {
                    "screen_name": screen_name,
                    "universe_size": 0,
                    "passed_count": 0,
                    "filters_applied": [
                        "close_gte_min_close",
                        "avg_volume_gte_min_avg_volume",
                    ],
                    "candidates": [],
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
                "worker_name": "screening_worker",
                "result": {
                    "screen_name": screen_name,
                    "universe_size": 0,
                    "passed_count": 0,
                    "filters_applied": [
                        "close_gte_min_close",
                        "avg_volume_gte_min_avg_volume",
                    ],
                    "candidates": [],
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
                "worker_name": "screening_worker",
                "result": {
                    "screen_name": screen_name,
                    "universe_size": 0,
                    "passed_count": 0,
                    "filters_applied": [
                        "close_gte_min_close",
                        "avg_volume_gte_min_avg_volume",
                    ],
                    "candidates": [],
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

        grouped = self._group_rows_by_ticker(rows)
        trace.append(f"grouped rows into {len(grouped)} tickers")

        candidates: list[dict[str, Any]] = []
        for ticker, ticker_rows in grouped.items():
            normalized_rows = [self._normalize_row(row) for row in ticker_rows]
            latest_bar = normalized_rows[-1]
            avg_volume_3 = self._avg_volume(normalized_rows[-3:])

            passes_close = latest_bar["close"] is not None and latest_bar["close"] >= min_close
            passes_volume = avg_volume_3 is not None and avg_volume_3 >= min_avg_volume

            if passes_close and passes_volume:
                score = float(latest_bar["close"]) + (avg_volume_3 / 1_000_000.0)
                candidates.append(
                    {
                        "ticker": ticker,
                        "rank": 0,  # filled later
                        "reason_codes": [
                            "close_gte_min_close",
                            "avg_volume_gte_min_avg_volume",
                        ],
                        "metrics": {
                            "close": latest_bar["close"],
                            "avg_volume_3": avg_volume_3,
                            "bars_available": len(normalized_rows),
                        },
                        "score": round(score, 4),
                    }
                )

        candidates.sort(key=lambda item: item["score"], reverse=True)
        candidates = candidates[:top_n]
        for idx, candidate in enumerate(candidates, start=1):
            candidate["rank"] = idx

        if not candidates:
            warnings.append("screen produced no passing candidates")

        confidence = 0.88 if candidates else 0.55

        payload = {
            "worker_name": "screening_worker",
            "result": {
                "screen_name": screen_name,
                "universe_size": len(grouped),
                "passed_count": len(candidates),
                "filters_applied": [
                    "close_gte_min_close",
                    "avg_volume_gte_min_avg_volume",
                ],
                "candidates": candidates,
                "data_source": str(path),
                "integrity_checks": {
                    "file_exists": True,
                    "required_columns_present": True,
                },
            },
            "confidence": confidence,
            "assumptions": assumptions,
            "warnings": warnings,
            "trace": trace + ["screened candidates and returned ranked subset"],
            "proposed_memory_update": None,
        }
        return self.validator.validate(payload)

    def _load_csv_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]

    def _group_rows_by_ticker(self, rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            ticker = str(row.get("ticker", "")).upper()
            if not ticker:
                continue
            grouped.setdefault(ticker, []).append(row)
        return grouped

    def _normalize_row(self, row: dict[str, str]) -> dict[str, Any]:
        return {
            "date": str(row.get("date", "")),
            "open": self._to_float(row.get("open")),
            "high": self._to_float(row.get("high")),
            "low": self._to_float(row.get("low")),
            "close": self._to_float(row.get("close")),
            "volume": self._to_int(row.get("volume")),
        }

    @staticmethod
    def _avg_volume(rows: list[dict[str, Any]]) -> int | None:
        volumes = [row["volume"] for row in rows if row["volume"] is not None]
        if not volumes:
            return None
        return int(sum(volumes) / len(volumes))

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
