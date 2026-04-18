from __future__ import annotations

from workers.trade_memo_worker import TradeMemoWorker


def build_memo_payload(*ticker_inputs: dict[str, object], memo_mode: str = "lite") -> dict[str, object]:
    return {
        "data": {
            "memo_mode": memo_mode,
            "ticker_inputs": list(ticker_inputs),
        }
    }


def test_trade_memo_worker_returns_lite_memo_structure() -> None:
    worker = TradeMemoWorker()
    payload = worker.run(
        memo_payload=build_memo_payload(
            {
                "ticker": "PVD",
                "sector": "oil_gas",
                "sector_state": "ACTIVE",
                "current_price": 28.7,
                "trend_quality_score": 8.5,
                "volume_confirmation_score": 8.0,
                "setup_readiness_score": 8.7,
                "final_score": 8.4,
                "setup_type": "base_breakout",
                "why_in": ["strong_close", "volume_expansion", "sector_active"],
                "why_not_top": [],
                "risk_note": ["near_short_term_resistance"],
                "support_zone": "27.6-28.0",
                "resistance_zone": "29.2-29.8",
                "ma20": 27.9,
                "ma50": 26.8,
                "ma200": 24.4,
                "rsi": 61.5,
                "macd_state": "bullish_turning_up",
                "structure_note": "tight base, fresh breakout attempt",
                "catalyst_note": "oil narrative + sector state active",
            }
        )
    )

    assert payload["worker_name"] == "trade_memo_worker"
    assert payload["result"]["memo_mode_requested"] == "lite"
    assert payload["result"]["memo_mode_effective"] == "lite"
    assert len(payload["result"]["ticker_memos"]) == 1
    assert len(payload["result"]["ticker_memos"][0]["scenario_table"]) == 3


def test_trade_memo_worker_keeps_thin_input_cautious() -> None:
    worker = TradeMemoWorker()
    payload = worker.run(
        memo_payload=build_memo_payload(
            {
                "ticker": "DPM",
                "sector": "fertilizer",
                "sector_state": "WATCH",
                "current_price": 36.4,
                "trend_quality_score": 6.4,
                "volume_confirmation_score": 5.4,
                "setup_readiness_score": 6.2,
                "why_in": ["base_ok", "sector_watch"],
                "why_not_top": ["needs_volume_confirmation"],
                "risk_note": ["still_under_resistance"],
                "support_zone": "35.0-35.5",
                "resistance_zone": "37.0-37.8",
            }
        )
    )

    memo = payload["result"]["ticker_memos"][0]
    probabilities = [row["probability_pct"] for row in memo["scenario_table"]]
    assert memo["setup_summary"]["status"] in {"watch_setup", "thin_setup"}
    assert memo["action_today"]["stance"] in {"watch_only", "watch_or_partial_entry", "avoid_for_now"}
    assert probabilities == [40, 35, 25] or probabilities == [30, 35, 35]


def test_trade_memo_worker_downshifts_full_mode_honestly() -> None:
    worker = TradeMemoWorker()
    payload = worker.run(
        memo_payload=build_memo_payload(
            {
                "ticker": "PVD",
                "sector": "oil_gas",
                "sector_state": "ACTIVE",
                "current_price": 28.7,
                "trend_quality_score": 8.5,
                "volume_confirmation_score": 8.0,
                "setup_readiness_score": 8.7,
                "why_in": ["strong_close", "volume_expansion", "sector_active"],
                "risk_note": ["near_short_term_resistance"],
                "support_zone": "27.6-28.0",
                "resistance_zone": "29.2-29.8",
            },
            memo_mode="full",
        )
    )

    assert payload["result"]["memo_mode_requested"] == "full"
    assert payload["result"]["memo_mode_effective"] == "lite"
    assert any("full-mode extras" in warning for warning in payload["warnings"])


def test_trade_memo_worker_is_honest_when_input_missing() -> None:
    worker = TradeMemoWorker()
    payload = worker.run(memo_payload=None)

    assert payload["result"]["input_status"] == "missing"
    assert payload["result"]["ticker_memos"] == []
    assert payload["confidence"] == 0.0
