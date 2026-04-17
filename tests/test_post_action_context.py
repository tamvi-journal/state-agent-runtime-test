from __future__ import annotations

from pathlib import Path

from context.context_view import ContextViewBuilder
from core.main_brain import MainBrain
from observability.logger import EventLogger
from observability.trace_events import TraceEvents
from runtime.execution_gate import ExecutionGate
from state.live_state import LiveState
from state.state_manager import StateManager
from verification.verification_loop import VerificationLoop
from workers.market_data_worker import MarketDataWorker


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
        user_signal="test post-action context",
        continuity_anchor="pytest-post-context",
        archive_needed=False,
    )
    return MainBrain(state_manager=StateManager(live_state=live_state))


def test_post_action_context_contains_verification_fields(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    main_brain = build_main_brain()
    logger = EventLogger()
    trace_events = TraceEvents(logger=logger)
    gate = ExecutionGate(
        market_data_worker=MarketDataWorker(data_path=csv_path),
        verification_loop=VerificationLoop(),
        trace_events=trace_events,
    )
    context_builder = ContextViewBuilder()

    payload, verification_record = gate.run_market_data_flow(ticker="MBB", timeframe="1D")

    post_action_context = context_builder.build_post_action(
        live_state=main_brain.get_live_state(),
        task_focus="completed first bounded market-data worker demo",
        current_environment_state=f"sample_csv_exists={csv_path.exists()}",
        verification_record=verification_record,
        open_obligations=["synthesize final answer"],
        current_risk="keep final answer bounded and non-judgmental",
        action_summary="market_data_worker executed for ticker=MBB",
    )
    trace_events.log_context_view(context_view=post_action_context)

    context_events = logger.by_category("context_view")
    assert len(context_events) >= 1

    latest_context = context_events[-1]["payload"]
    assert latest_context["context_phase"] == "post_action"
    assert latest_context["verification_status"] == "passed"
    assert "observed_outcome" in latest_context
    assert latest_context["action_summary"] == "market_data_worker executed for ticker=MBB"

    assert payload["result"]["bars_found"] == 3
