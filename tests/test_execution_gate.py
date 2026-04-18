from __future__ import annotations

from pathlib import Path

from gate.execution_gate import ExecutionGate
from observability.logger import EventLogger
from observability.trace_events import TraceEvents
from tools.market_data_tool import MarketDataTool
from verification.verification_loop import VerificationLoop
from workers.candle_volume_structure_worker import CandleVolumeStructureWorker
from workers.macro_sector_mapping_worker import MacroSectorMappingWorker
from workers.market_data_worker import MarketDataWorker
from workers.sector_flow_worker import SectorFlowWorker
from workers.technical_analysis_worker import TechnicalAnalysisWorker
from workers.trade_memo_worker import TradeMemoWorker


def _write_csv(path: Path) -> None:
    path.write_text(
        "date,ticker,open,high,low,close,volume\n"
        "2026-04-08,MBB,24.6,24.9,24.4,24.8,14500000\n"
        "2026-04-09,MBB,24.8,25.0,24.7,24.9,16200000\n"
        "2026-04-10,MBB,24.8,25.2,24.6,25.1,18450200\n",
        encoding="utf-8",
    )


def _build_gate(csv_path: Path) -> ExecutionGate:
    return ExecutionGate(
        market_data_worker=MarketDataWorker(market_data_tool=MarketDataTool(data_path=csv_path)),
        technical_analysis_worker=TechnicalAnalysisWorker(market_data_tool=MarketDataTool(data_path=csv_path)),
        macro_sector_mapping_worker=MacroSectorMappingWorker(),
        sector_flow_worker=SectorFlowWorker(),
        candle_volume_structure_worker=CandleVolumeStructureWorker(),
        trade_memo_worker=TradeMemoWorker(),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=EventLogger()),
    )


def test_market_data_lookup_is_sandbox_only(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    _write_csv(csv_path)

    gate = _build_gate(csv_path)
    decision = gate.decide(action_name="market_data_lookup")

    assert decision.decision == "sandbox_only"
    assert "bounded harness surface" in decision.reason


def test_mutating_actions_need_approval(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    _write_csv(csv_path)

    gate = _build_gate(csv_path)

    assert gate.decide(action_name="write_file").decision == "needs_approval"
    assert gate.decide(action_name="network_access").decision == "needs_approval"


def test_unsupported_actions_are_denied(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    _write_csv(csv_path)

    gate = _build_gate(csv_path)
    decision = gate.decide(action_name="archive_replay")

    assert decision.decision == "deny"


def test_gate_executes_market_data_and_returns_verification(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    _write_csv(csv_path)

    gate = _build_gate(csv_path)
    decision, payload, record = gate.run_market_data_flow(ticker="MBB", timeframe="1D")

    assert decision.decision == "sandbox_only"
    assert payload is not None
    assert record is not None
    assert payload["result"]["bars_found"] == 3
    assert record.verification_status == "passed"
    assert "market_data_tool.load_market_data" in record.executed_action


def test_verification_fails_when_ticker_is_missing(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    _write_csv(csv_path)

    gate = _build_gate(csv_path)
    _, payload, record = gate.run_market_data_flow(ticker="VCB", timeframe="1D")

    assert payload is not None
    assert payload["result"]["bars_found"] == 0
    assert record is not None
    assert record.verification_status == "failed"


def test_gate_executes_sector_flow_and_returns_verification(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    _write_csv(csv_path)

    gate = _build_gate(csv_path)
    decision, payload, record = gate.run_sector_flow(
        sector_flow_payload={
            "data": {
                "benchmark": {"ticker": "VNINDEX", "change_pct": 0.52},
                "sector_metrics": [
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
                ],
            }
        }
    )

    assert decision.decision == "sandbox_only"
    assert payload is not None
    assert record is not None
    assert payload["result"]["sector_flow_board"][0]["state"] == "HOT"
    assert record.verification_status == "passed"
    assert "sector_flow_worker.run" in record.executed_action


def test_gate_executes_candle_volume_structure_and_returns_verification(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    _write_csv(csv_path)

    gate = _build_gate(csv_path)
    decision, payload, record = gate.run_candle_volume_structure(
        candidate_payload={
            "data": {
                "stock_candidates": [
                    {
                        "ticker": "PVD",
                        "sector": "oil_gas",
                        "sector_state": "ACTIVE",
                        "avg_trading_value_20d_bil_vnd": 18.0,
                        "avg_volume_20d": 1200000,
                        "rs_score": 81,
                        "price_structure_ok": True,
                        "warning_status": "normal",
                        "close_below_ma50_pct": 1.0,
                        "breakdown_confirmed": False,
                        "distance_to_recent_support_pct": 4.0,
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
                    }
                ]
            }
        }
    )

    assert decision.decision == "sandbox_only"
    assert payload is not None
    assert record is not None
    assert payload["result"]["top_list"][0]["ticker"] == "PVD"
    assert record.verification_status == "passed"
    assert "candle_volume_structure_worker.run" in record.executed_action


def test_gate_executes_trade_memo_and_returns_verification(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    _write_csv(csv_path)

    gate = _build_gate(csv_path)
    decision, payload, record = gate.run_trade_memo(
        memo_payload={
            "data": {
                "memo_mode": "lite",
                "ticker_inputs": [
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
                    }
                ],
            }
        }
    )

    assert decision.decision == "sandbox_only"
    assert payload is not None
    assert record is not None
    assert payload["result"]["ticker_memos"][0]["ticker"] == "PVD"
    assert record.verification_status == "passed"
    assert "trade_memo_worker.run" in record.executed_action
