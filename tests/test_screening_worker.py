from __future__ import annotations

from pathlib import Path

from workers.screening_worker import ScreeningWorker


def write_csv(path: Path) -> None:
    path.write_text(
        "date,ticker,open,high,low,close,volume\n"
        "2026-04-08,MBB,24.6,24.9,24.4,24.8,14500000\n"
        "2026-04-09,MBB,24.8,25.0,24.7,24.9,16200000\n"
        "2026-04-10,MBB,24.8,25.2,24.6,25.1,18450200\n"
        "2026-04-08,VCI,40.1,40.8,39.9,40.5,8200000\n"
        "2026-04-09,VCI,40.5,41.0,40.3,40.7,9000000\n"
        "2026-04-10,VCI,40.7,41.5,40.6,41.3,9642100\n"
        "2026-04-08,AAA,8.1,8.3,8.0,8.2,1200000\n"
        "2026-04-09,AAA,8.2,8.4,8.1,8.3,1300000\n"
        "2026-04-10,AAA,8.3,8.5,8.2,8.4,1250000\n",
        encoding="utf-8",
    )


def test_screening_worker_returns_ranked_candidates(tmp_path: Path) -> None:
    csv_path = tmp_path / "screening_data.csv"
    write_csv(csv_path)

    worker = ScreeningWorker(data_path=csv_path)
    payload = worker.run(min_close=10.0, min_avg_volume=5_000_000, top_n=5)

    assert payload["worker_name"] == "screening_worker"
    assert payload["confidence"] > 0.0
    assert payload["result"]["screen_name"] == "close_volume_basic_v1"
    assert payload["result"]["universe_size"] == 3
    assert payload["result"]["passed_count"] == 2

    candidates = payload["result"]["candidates"]
    assert len(candidates) == 2
    assert candidates[0]["rank"] == 1
    assert candidates[0]["ticker"] in {"MBB", "VCI"}
    assert "reason_codes" in candidates[0]
    assert "metrics" in candidates[0]


def test_screening_worker_handles_missing_file(tmp_path: Path) -> None:
    csv_path = tmp_path / "missing.csv"

    worker = ScreeningWorker(data_path=csv_path)
    payload = worker.run()

    assert payload["worker_name"] == "screening_worker"
    assert payload["confidence"] == 0.0
    assert payload["result"]["universe_size"] == 0
    assert payload["result"]["integrity_checks"]["file_exists"] is False


def test_screening_worker_returns_no_candidates_when_filters_too_strict(tmp_path: Path) -> None:
    csv_path = tmp_path / "screening_data.csv"
    write_csv(csv_path)

    worker = ScreeningWorker(data_path=csv_path)
    payload = worker.run(min_close=100.0, min_avg_volume=999_999_999, top_n=5)

    assert payload["result"]["passed_count"] == 0
    assert payload["result"]["candidates"] == []
    assert "screen produced no passing candidates" in payload["warnings"]
