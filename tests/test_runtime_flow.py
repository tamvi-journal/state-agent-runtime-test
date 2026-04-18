from __future__ import annotations

from pathlib import Path

from brain.main_brain import MainBrain
from observability.logger import EventLogger
from observability.trace_events import TraceEvents
from gate.execution_gate import ExecutionGate
from runtime.request_router import RequestRouter
from state.live_state import LiveState
from state.state_manager import StateManager
from tools.market_data_tool import MarketDataTool
from verification.verification_loop import VerificationLoop
from workers.candle_volume_structure_worker import CandleVolumeStructureWorker
from workers.macro_sector_mapping_worker import MacroSectorMappingWorker
from workers.market_data_worker import MarketDataWorker
from workers.sector_flow_worker import SectorFlowWorker
from workers.technical_analysis_worker import TechnicalAnalysisWorker
from workers.trade_memo_worker import TradeMemoWorker


def write_csv(path: Path) -> None:
    path.write_text(
        "date,ticker,open,high,low,close,volume\n"
        "2026-04-08,MBB,24.6,24.9,24.4,24.8,14500000\n"
        "2026-04-09,MBB,24.8,25.0,24.7,24.9,16200000\n"
        "2026-04-10,MBB,24.8,25.2,24.6,25.1,18450200\n",
        encoding="utf-8",
    )


def build_main_brain() -> MainBrain:
    live_state = LiveState(
        active_mode="build",
        current_axis="technical",
        coherence_level=0.92,
        tension_flags=[],
        active_project="state-memory-agent",
        user_signal="test runtime flow",
        continuity_anchor="pytest-flow",
        archive_needed=False,
    )
    return MainBrain(state_manager=StateManager(live_state=live_state))


def test_runtime_flow_happy_path(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    main_brain = build_main_brain()
    router = RequestRouter(main_brain=main_brain)

    logger = EventLogger()
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(market_data_tool=MarketDataTool(data_path=csv_path)),
        technical_analysis_worker=TechnicalAnalysisWorker(market_data_tool=MarketDataTool(data_path=csv_path)),
        macro_sector_mapping_worker=MacroSectorMappingWorker(),
        sector_flow_worker=SectorFlowWorker(),
        candle_volume_structure_worker=CandleVolumeStructureWorker(),
        trade_memo_worker=TradeMemoWorker(),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=logger),
    )

    interpreted = main_brain.interpret_request("Load MBB daily data")
    assert interpreted["needs_worker"] is True
    assert interpreted["ticker"] == "MBB"

    _, payload, verification_record = gate.run_market_data_flow(ticker="MBB", timeframe="1D")
    final_response = router.route(
        "Load MBB daily data",
        worker_payload=payload,
        verification_record=verification_record,
    )

    assert "I checked MBB using market_data_worker." in final_response
    assert "Verification passed." in final_response
    assert "Latest daily bar:" in final_response
    assert verification_record is not None
    assert "market_data_worker may call market_data_tool.load_market_data" in verification_record.intended_action
    assert "execution path ran market_data_worker.run -> market_data_tool.load_market_data" in verification_record.executed_action


def test_runtime_flow_failure_path(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    main_brain = build_main_brain()
    router = RequestRouter(main_brain=main_brain)

    logger = EventLogger()
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(market_data_tool=MarketDataTool(data_path=csv_path)),
        technical_analysis_worker=TechnicalAnalysisWorker(market_data_tool=MarketDataTool(data_path=csv_path)),
        macro_sector_mapping_worker=MacroSectorMappingWorker(),
        sector_flow_worker=SectorFlowWorker(),
        candle_volume_structure_worker=CandleVolumeStructureWorker(),
        trade_memo_worker=TradeMemoWorker(),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=logger),
    )

    _, payload, verification_record = gate.run_market_data_flow(ticker="VCB", timeframe="1D")
    final_response = router.route(
        "Load VCB daily data",
        worker_payload=payload,
        verification_record=verification_record,
    )

    assert "Verification failed." in final_response
    assert "No bars were returned for this ticker in the current dataset." in final_response


def test_runtime_flow_technical_analysis_path(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    main_brain = build_main_brain()
    router = RequestRouter(main_brain=main_brain)

    logger = EventLogger()
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(market_data_tool=MarketDataTool(data_path=csv_path)),
        technical_analysis_worker=TechnicalAnalysisWorker(market_data_tool=MarketDataTool(data_path=csv_path)),
        macro_sector_mapping_worker=MacroSectorMappingWorker(),
        sector_flow_worker=SectorFlowWorker(),
        candle_volume_structure_worker=CandleVolumeStructureWorker(),
        trade_memo_worker=TradeMemoWorker(),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=logger),
    )

    interpreted = main_brain.interpret_request("technical analysis for MBB")
    assert interpreted["needs_worker"] is True
    assert interpreted["worker_name"] == "technical_analysis_worker"
    assert interpreted["task_type"] == "technical_analysis"

    _, payload, verification_record = gate.run_technical_analysis_flow(ticker="MBB", timeframe="1D")
    final_response = router.route(
        "technical analysis for MBB",
        worker_payload=payload,
        verification_record=verification_record,
    )

    assert payload is not None
    assert payload["result"]["alignment_status"] in {"bullish", "bearish", "mixed", "range", "unresolved"}
    assert verification_record is not None
    assert "technical_analysis_worker may call market_data_tool.load_market_data" in verification_record.intended_action
    assert "bounded technical-analysis read" in final_response


def test_runtime_flow_macro_sector_mapping_path_uses_explicit_input() -> None:
    main_brain = build_main_brain()
    router = RequestRouter(main_brain=main_brain)

    logger = EventLogger()
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(market_data_tool=MarketDataTool(data_path="data/sample_market_data.csv")),
        technical_analysis_worker=TechnicalAnalysisWorker(market_data_tool=MarketDataTool(data_path="data/sample_market_data.csv")),
        macro_sector_mapping_worker=MacroSectorMappingWorker(),
        sector_flow_worker=SectorFlowWorker(),
        candle_volume_structure_worker=CandleVolumeStructureWorker(),
        trade_memo_worker=TradeMemoWorker(),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=logger),
    )

    interpreted = main_brain.interpret_request("macro sector mapping")
    assert interpreted["needs_worker"] is True
    assert interpreted["worker_name"] == "macro_sector_mapping_worker"
    assert interpreted["task_type"] == "macro_sector_mapping"

    _, payload, verification_record = gate.run_macro_sector_mapping_flow(
        macro_signal_payload={
            "data": {
                "scan_date": "2026-03-29",
                "global_signals": [
                    {
                        "signal_id": "oil_001",
                        "theme": "oil",
                        "headline": "Brent rises on Middle East tension",
                        "summary": "Oil extended gains after renewed geopolitical tension.",
                        "direction": "positive",
                        "strength_score": 8.4,
                        "confidence": "high",
                        "time_horizon": "short_term",
                        "source": "Reuters",
                    }
                ],
            }
        }
    )
    final_response = router.route(
        "macro sector mapping",
        worker_payload=payload,
        verification_record=verification_record,
    )

    assert payload is not None
    assert payload["result"]["matched_signals"][0]["matched_trigger"] == "oil_up"
    assert verification_record is not None
    assert "macro_sector_mapping_worker may use explicit normalized macro input" in verification_record.intended_action
    assert "bounded macro-sector mapping evidence" in final_response


def test_runtime_flow_sector_flow_path_uses_explicit_input() -> None:
    main_brain = build_main_brain()
    router = RequestRouter(main_brain=main_brain)

    logger = EventLogger()
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(market_data_tool=MarketDataTool(data_path="data/sample_market_data.csv")),
        technical_analysis_worker=TechnicalAnalysisWorker(market_data_tool=MarketDataTool(data_path="data/sample_market_data.csv")),
        macro_sector_mapping_worker=MacroSectorMappingWorker(),
        sector_flow_worker=SectorFlowWorker(),
        candle_volume_structure_worker=CandleVolumeStructureWorker(),
        trade_memo_worker=TradeMemoWorker(),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=logger),
    )

    interpreted = main_brain.interpret_request("sector flow")
    assert interpreted["needs_worker"] is True
    assert interpreted["worker_name"] == "sector_flow_worker"
    assert interpreted["task_type"] == "sector_flow"

    _, payload, verification_record = gate.run_sector_flow(
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
        },
        macro_sector_bias_payload={
            "data": {
                "vn_sector_bias": [
                    {
                        "sector": "oil_gas",
                        "direction": "positive",
                        "reason": "oil_up",
                    }
                ]
            }
        },
    )
    final_response = router.route(
        "sector flow",
        worker_payload=payload,
        verification_record=verification_record,
    )

    assert payload is not None
    assert payload["result"]["sector_flow_board"][0]["state"] == "HOT"
    assert verification_record is not None
    assert "sector_flow_worker may classify explicit sector metrics" in verification_record.intended_action
    assert "bounded sector-flow evidence" in final_response


def test_runtime_flow_candle_volume_structure_path_uses_explicit_input() -> None:
    main_brain = build_main_brain()
    router = RequestRouter(main_brain=main_brain)

    logger = EventLogger()
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(market_data_tool=MarketDataTool(data_path="data/sample_market_data.csv")),
        technical_analysis_worker=TechnicalAnalysisWorker(market_data_tool=MarketDataTool(data_path="data/sample_market_data.csv")),
        macro_sector_mapping_worker=MacroSectorMappingWorker(),
        sector_flow_worker=SectorFlowWorker(),
        candle_volume_structure_worker=CandleVolumeStructureWorker(),
        trade_memo_worker=TradeMemoWorker(),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=logger),
    )

    interpreted = main_brain.interpret_request("candle volume structure")
    assert interpreted["needs_worker"] is True
    assert interpreted["worker_name"] == "candle_volume_structure_worker"
    assert interpreted["task_type"] == "candle_volume_structure"

    _, payload, verification_record = gate.run_candle_volume_structure(
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
    final_response = router.route(
        "candle volume structure",
        worker_payload=payload,
        verification_record=verification_record,
    )

    assert payload is not None
    assert payload["result"]["top_list"][0]["ticker"] == "PVD"
    assert verification_record is not None
    assert "candle_volume_structure_worker may score explicit stock candidates" in verification_record.intended_action
    assert "bounded setup evidence" in final_response


def test_runtime_flow_trade_memo_path_uses_explicit_input() -> None:
    main_brain = build_main_brain()
    router = RequestRouter(main_brain=main_brain)

    logger = EventLogger()
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(market_data_tool=MarketDataTool(data_path="data/sample_market_data.csv")),
        technical_analysis_worker=TechnicalAnalysisWorker(market_data_tool=MarketDataTool(data_path="data/sample_market_data.csv")),
        macro_sector_mapping_worker=MacroSectorMappingWorker(),
        sector_flow_worker=SectorFlowWorker(),
        candle_volume_structure_worker=CandleVolumeStructureWorker(),
        trade_memo_worker=TradeMemoWorker(),
        verification_loop=VerificationLoop(),
        trace_events=TraceEvents(logger=logger),
    )

    interpreted = main_brain.interpret_request("trade memo")
    assert interpreted["needs_worker"] is True
    assert interpreted["worker_name"] == "trade_memo_worker"
    assert interpreted["task_type"] == "trade_memo"

    _, payload, verification_record = gate.run_trade_memo(
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
    final_response = router.route(
        "trade memo",
        worker_payload=payload,
        verification_record=verification_record,
    )

    assert payload is not None
    assert payload["result"]["ticker_memos"][0]["ticker"] == "PVD"
    assert verification_record is not None
    assert "trade_memo_worker may build bounded scenario memo evidence" in verification_record.intended_action
    assert "bounded trade-memo evidence" in final_response
