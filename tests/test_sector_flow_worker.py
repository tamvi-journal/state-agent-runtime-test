from __future__ import annotations

from pathlib import Path

from workers.sector_flow_worker import SectorFlowWorker


def build_sector_payload(*metrics: dict[str, object]) -> dict[str, object]:
    return {
        "data": {
            "benchmark": {"ticker": "VNINDEX", "change_pct": 0.52},
            "sector_metrics": list(metrics),
        }
    }


def test_sector_flow_worker_returns_structured_evidence() -> None:
    worker = SectorFlowWorker()
    payload = worker.run(
        sector_flow_payload=build_sector_payload(
            {
                "sector": "oil_gas",
                "rs_score": 82,
                "volume_ratio_vs_ma20": 1.62,
                "breadth_score": 8.0,
                "up_down_ratio": 3.4,
                "breakout_count": 4,
                "breakdown_count": 0,
                "leader_count": 3,
                "macro_alignment": True,
            }
        )
    )

    assert payload["worker_name"] == "sector_flow_worker"
    assert payload["result"]["input_status"] == "loaded"
    assert payload["result"]["sector_flow_board"][0]["sector"] == "oil_gas"
    assert payload["result"]["sector_flow_board"][0]["state"] == "HOT"
    assert payload["confidence"] > 0.0


def test_sector_flow_worker_classifies_watch_active_hot_and_weakening() -> None:
    worker = SectorFlowWorker()
    payload = worker.run(
        sector_flow_payload=build_sector_payload(
            {
                "sector": "fertilizer",
                "rs_score": 61,
                "volume_ratio_vs_ma20": 0.96,
                "breadth_score": 5.8,
                "up_down_ratio": 1.6,
                "breakout_count": 1,
                "breakdown_count": 0,
                "leader_count": 1,
                "macro_alignment": True,
            },
            {
                "sector": "steel",
                "rs_score": 68,
                "volume_ratio_vs_ma20": 1.2,
                "breadth_score": 6.8,
                "up_down_ratio": 1.7,
                "breakout_count": 1,
                "breakdown_count": 0,
                "leader_count": 2,
                "macro_alignment": True,
            },
            {
                "sector": "oil_gas",
                "rs_score": 82,
                "volume_ratio_vs_ma20": 1.62,
                "breadth_score": 8.0,
                "up_down_ratio": 3.4,
                "breakout_count": 4,
                "breakdown_count": 0,
                "leader_count": 3,
                "macro_alignment": True,
            },
            {
                "sector": "airlines",
                "rs_score": 57,
                "volume_ratio_vs_ma20": 1.05,
                "breadth_score": 4.2,
                "up_down_ratio": 0.7,
                "breakout_count": 0,
                "breakdown_count": 2,
                "leader_count": 0,
                "macro_alignment": True,
            },
        )
    )

    board = {entry["sector"]: entry["state"] for entry in payload["result"]["sector_flow_board"]}
    assert board["fertilizer"] == "WATCH"
    assert board["steel"] == "ACTIVE"
    assert board["oil_gas"] == "HOT"
    assert board["airlines"] == "WEAKENING"


def test_sector_flow_worker_keeps_weakening_first_class_when_watch_like_signals_exist() -> None:
    worker = SectorFlowWorker()
    payload = worker.run(
        sector_flow_payload=build_sector_payload(
            {
                "sector": "airlines",
                "rs_score": 58,
                "volume_ratio_vs_ma20": 0.95,
                "breadth_score": 4.6,
                "up_down_ratio": 1.25,
                "breakout_count": 1,
                "breakdown_count": 2,
                "leader_count": 1,
                "macro_alignment": True,
                "prior_state": "ACTIVE",
                "rs_score_drop_3d": 6.0,
            }
        )
    )

    entry = payload["result"]["sector_flow_board"][0]
    assert entry["state"] == "WEAKENING"


def test_sector_flow_worker_preserves_macro_flow_conflict() -> None:
    worker = SectorFlowWorker()
    payload = worker.run(
        sector_flow_payload=build_sector_payload(
            {
                "sector": "airlines",
                "rs_score": 44,
                "volume_ratio_vs_ma20": 1.08,
                "breadth_score": 4.2,
                "up_down_ratio": 0.7,
                "breakout_count": 0,
                "breakdown_count": 2,
                "leader_count": 0,
                "macro_alignment": True,
            }
        ),
        macro_sector_bias_payload={
            "data": {
                "vn_sector_bias": [
                    {
                        "sector": "airlines",
                        "direction": "positive",
                        "reason": "oil_down",
                    }
                ]
            }
        },
    )

    entry = payload["result"]["sector_flow_board"][0]
    assert entry["state"] == "WEAKENING"
    assert entry["conflict_flag"] is True
    assert any(flag["sector"] == "airlines" for flag in payload["result"]["conflict_flags"])


def test_sector_flow_worker_does_not_invent_sectors() -> None:
    worker = SectorFlowWorker()
    payload = worker.run(
        sector_flow_payload=build_sector_payload(
            {
                "sector": "imaginary_sector",
                "rs_score": 82,
                "volume_ratio_vs_ma20": 1.62,
                "breadth_score": 8.0,
                "up_down_ratio": 3.4,
                "breakout_count": 4,
                "breakdown_count": 0,
                "leader_count": 3,
                "macro_alignment": True,
            }
        )
    )

    assert payload["result"]["sector_flow_board"] == []
    assert payload["result"]["unclassified_sectors"][0]["sector"] == "imaginary_sector"


def test_sector_flow_worker_is_honest_when_input_missing() -> None:
    worker = SectorFlowWorker()
    payload = worker.run(sector_flow_payload=None)

    assert payload["result"]["input_status"] == "missing"
    assert payload["result"]["sector_flow_board"] == []
    assert payload["confidence"] == 0.0


def test_sector_flow_worker_is_honest_when_config_missing(tmp_path: Path) -> None:
    worker = SectorFlowWorker(
        state_rules_path=tmp_path / "missing_state_rules.json",
        sector_universe_path=tmp_path / "missing_sector_universe.json",
    )
    payload = worker.run(
        sector_flow_payload=build_sector_payload(
            {
                "sector": "oil_gas",
                "rs_score": 82,
                "volume_ratio_vs_ma20": 1.62,
                "breadth_score": 8.0,
                "up_down_ratio": 3.4,
                "breakout_count": 4,
                "breakdown_count": 0,
                "leader_count": 3,
                "macro_alignment": True,
            }
        )
    )

    assert payload["result"]["input_status"] == "missing"
    assert payload["result"]["sector_flow_board"] == []
    assert payload["confidence"] == 0.0
    assert any("canonical sector state rules" in warning or "canonical sector universe" in warning for warning in payload["warnings"])
