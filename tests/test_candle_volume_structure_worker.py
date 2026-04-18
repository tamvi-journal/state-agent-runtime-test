from __future__ import annotations

from pathlib import Path

from workers.candle_volume_structure_worker import CandleVolumeStructureWorker


def build_candidate_payload(*candidates: dict[str, object]) -> dict[str, object]:
    return {
        "data": {
            "stock_candidates": list(candidates),
        }
    }


def test_candle_volume_structure_worker_returns_structured_evidence() -> None:
    worker = CandleVolumeStructureWorker()
    payload = worker.run(
        candidate_payload=build_candidate_payload(
            {
                "ticker": "PVD",
                "sector": "oil_gas",
                "sector_state": "ACTIVE",
                "avg_trading_value_20d_bil_vnd": 18.0,
                "avg_volume_20d": 1200000,
                "rs_score": 81,
                "price_structure_ok": True,
                "warning_status": "normal",
                "close_below_ma50_pct": 1.5,
                "breakdown_confirmed": False,
                "distance_to_recent_support_pct": 4.5,
                "support_status": "safe",
                "candidate_reason": ["sector_active", "rs_strong", "structure_intact"],
                "ohlcv_context": {
                    "setup_type": "base_breakout",
                    "location_type": "above_support",
                    "candle_signal": "bullish_momentum",
                    "close_quality": "strong_close_near_high",
                    "volume_signal": "expanded_confirmed",
                    "base_quality": "tight_base",
                    "retest_quality": "not_required",
                    "volume_vs_ma20": 1.45,
                    "recent_structure_note": "base breakout with constructive follow-through",
                },
            }
        )
    )

    assert payload["worker_name"] == "candle_volume_structure_worker"
    assert payload["result"]["input_status"] == "loaded"
    assert payload["result"]["top_list"][0]["ticker"] == "PVD"
    assert payload["confidence"] > 0.0


def test_candle_volume_structure_worker_keeps_top_watch_and_reject_distinct() -> None:
    worker = CandleVolumeStructureWorker()
    payload = worker.run(
        candidate_payload=build_candidate_payload(
            {
                "ticker": "PVD",
                "sector": "oil_gas",
                "sector_state": "ACTIVE",
                "avg_trading_value_20d_bil_vnd": 18.0,
                "avg_volume_20d": 1200000,
                "rs_score": 81,
                "price_structure_ok": True,
                "warning_status": "normal",
                "close_below_ma50_pct": 1.5,
                "breakdown_confirmed": False,
                "distance_to_recent_support_pct": 4.5,
                "support_status": "safe",
                "candidate_reason": ["sector_active", "rs_strong", "structure_intact"],
                "ohlcv_context": {
                    "setup_type": "base_breakout",
                    "location_type": "above_support",
                    "candle_signal": "bullish_momentum",
                    "close_quality": "strong_close_near_high",
                    "volume_signal": "expanded_confirmed",
                    "base_quality": "tight_base",
                    "retest_quality": "not_required",
                    "volume_vs_ma20": 1.45,
                },
            },
            {
                "ticker": "DPM",
                "sector": "fertilizer",
                "sector_state": "WATCH",
                "avg_trading_value_20d_bil_vnd": 17.0,
                "avg_volume_20d": 800000,
                "rs_score": 64,
                "price_structure_ok": True,
                "warning_status": "normal",
                "close_below_ma50_pct": 0.0,
                "breakdown_confirmed": False,
                "distance_to_recent_support_pct": 3.0,
                "support_status": "safe",
                "candidate_reason": ["sector_watch", "base_forming"],
                "ohlcv_context": {
                    "setup_type": "base_forming",
                    "location_type": "near_resistance",
                    "candle_signal": "quiet_candle",
                    "close_quality": "neutral",
                    "volume_signal": "drying_up",
                    "base_quality": "acceptable",
                    "retest_quality": "pending",
                    "volume_vs_ma20": 0.82,
                    "recent_structure_note": "base forming under short-term resistance",
                },
            },
            {
                "ticker": "XYZ",
                "sector": "steel",
                "sector_state": "WATCH",
                "avg_trading_value_20d_bil_vnd": 4.0,
                "avg_volume_20d": 50000,
                "rs_score": 40,
                "price_structure_ok": False,
                "warning_status": "warning",
                "close_below_ma50_pct": -7.0,
                "breakdown_confirmed": True,
                "distance_to_recent_support_pct": 1.0,
                "support_status": "at_risk",
                "candidate_reason": [],
            },
        )
    )

    assert payload["result"]["top_list"][0]["ticker"] == "PVD"
    assert payload["result"]["watch_list"][0]["ticker"] == "DPM"
    assert payload["result"]["rejected"][0]["ticker"] == "XYZ"


def test_candle_volume_structure_worker_keeps_explainability_fields_visible() -> None:
    worker = CandleVolumeStructureWorker()
    payload = worker.run(
        candidate_payload=build_candidate_payload(
            {
                "ticker": "DPM",
                "sector": "fertilizer",
                "sector_state": "WATCH",
                "avg_trading_value_20d_bil_vnd": 17.0,
                "avg_volume_20d": 800000,
                "rs_score": 64,
                "price_structure_ok": True,
                "warning_status": "normal",
                "close_below_ma50_pct": 0.0,
                "breakdown_confirmed": False,
                "distance_to_recent_support_pct": 3.0,
                "support_status": "safe",
                "candidate_reason": ["sector_watch", "base_forming"],
                "ohlcv_context": {
                    "setup_type": "base_forming",
                    "location_type": "near_resistance",
                    "candle_signal": "quiet_candle",
                    "close_quality": "neutral",
                    "volume_signal": "drying_up",
                    "base_quality": "acceptable",
                    "retest_quality": "pending",
                    "volume_vs_ma20": 0.82,
                    "recent_structure_note": "base forming under short-term resistance",
                },
            }
        )
    )

    watch_entry = payload["result"]["watch_list"][0]
    assert "why_in" in watch_entry
    assert "why_not_top" in watch_entry
    assert "risk_note" in watch_entry
    assert watch_entry["why_not_top"]


def test_candle_volume_structure_worker_keeps_partial_context_honest() -> None:
    worker = CandleVolumeStructureWorker()
    payload = worker.run(
        candidate_payload=build_candidate_payload(
            {
                "ticker": "PVS",
                "sector": "oil_gas",
                "sector_state": "ACTIVE",
                "avg_trading_value_20d_bil_vnd": 17.5,
                "avg_volume_20d": 900000,
                "rs_score": 79,
                "price_structure_ok": True,
                "warning_status": "normal",
                "close_below_ma50_pct": 0.0,
                "breakdown_confirmed": False,
                "distance_to_recent_support_pct": 3.0,
                "support_status": "safe",
                "candidate_reason": ["sector_active", "rs_strong"],
            }
        )
    )

    assert payload["result"]["top_list"] == []
    assert payload["result"]["watch_list"][0]["ticker"] == "PVS"
    assert payload["result"]["watch_list"][0]["scores"]["final_score"] <= 7.0


def test_candle_volume_structure_worker_is_honest_when_input_missing() -> None:
    worker = CandleVolumeStructureWorker()
    payload = worker.run(candidate_payload=None)

    assert payload["result"]["input_status"] == "missing"
    assert payload["result"]["top_list"] == []
    assert payload["result"]["watch_list"] == []
    assert payload["confidence"] == 0.0


def test_candle_volume_structure_worker_is_honest_when_config_missing(tmp_path: Path) -> None:
    worker = CandleVolumeStructureWorker(hard_filter_rules_path=tmp_path / "missing_hard_filters.json")
    payload = worker.run(
        candidate_payload=build_candidate_payload(
            {
                "ticker": "PVD",
                "sector": "oil_gas",
                "sector_state": "ACTIVE",
                "avg_trading_value_20d_bil_vnd": 18.0,
                "avg_volume_20d": 1200000,
                "rs_score": 81,
                "price_structure_ok": True,
                "warning_status": "normal",
            }
        )
    )

    assert payload["result"]["input_status"] == "missing"
    assert payload["result"]["top_list"] == []
    assert payload["result"]["watch_list"] == []
    assert payload["confidence"] == 0.0
    assert any("canonical hard filter rules" in warning for warning in payload["warnings"])
