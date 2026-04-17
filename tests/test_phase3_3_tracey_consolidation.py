from __future__ import annotations

from pathlib import Path

from allocator.effort_allocator import EffortAllocator
from context.context_view import ContextViewBuilder
from core.main_brain import MainBrain
from family.shared_ontology import SharedOntology
from monitor.mirror_bridge import MirrorBridge
from monitor.monitor_layer import MonitorLayer
from observability.logger import EventLogger
from observability.trace_events import TraceEvents
from runtime.execution_gate import ExecutionGate
from runtime.governance_pass import GovernancePass
from runtime.request_router import RequestRouter
from runtime.tracey_runtime_pass import TraceyRuntimePass
from state.delta_log import DeltaRecord
from state.live_state import LiveState
from state.state_manager import StateManager
from tracey.tracey_adapter import TraceyAdapter
from tracey.tracey_axis import TraceyAxis
from tracey.tracey_memory import TraceyMemory
from tracey.tracey_runtime_profile import TraceyRuntimeProfile
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


def build_tracey_profile() -> TraceyRuntimeProfile:
    memory = TraceyMemory()
    memory.starter_set()
    return TraceyRuntimeProfile(
        axis=TraceyAxis(),
        memory=memory,
        ontology=SharedOntology(),
    )


def build_runtime():
    live_state = LiveState(
        active_mode="build",
        current_axis="technical",
        coherence_level=0.92,
        tension_flags=[],
        active_project="state-memory-agent",
        user_signal="test tracey consolidation",
        continuity_anchor="pytest-phase3-3",
        archive_needed=False,
    )
    state_manager = StateManager(live_state=live_state)
    state_manager.append_delta(
        DeltaRecord(
            mode_shift="",
            coherence_shift=0.0,
            policy_intrusion_detected=False,
            repair_event=False,
            trigger_cue="pytest_start",
            archive_consulted=False,
        )
    )

    logger = EventLogger()
    trace_events = TraceEvents(logger=logger)
    main_brain = MainBrain(state_manager=state_manager)
    router = RequestRouter(main_brain=main_brain)
    governance_pass = GovernancePass(
        monitor_layer=MonitorLayer(),
        mirror_bridge=MirrorBridge(),
        effort_allocator=EffortAllocator(),
    )
    tracey_runtime_pass = TraceyRuntimePass(
        adapter=TraceyAdapter(profile=build_tracey_profile()),
    )

    return (
        state_manager,
        main_brain,
        router,
        governance_pass,
        tracey_runtime_pass,
        trace_events,
        logger,
    )


def test_tracey_consolidation_logs_tracey_and_adapts_response(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample_market_data.csv"
    write_csv(csv_path)

    (
        state_manager,
        main_brain,
        router,
        governance_pass,
        tracey_runtime_pass,
        trace_events,
        logger,
    ) = build_runtime()

    execution_gate = ExecutionGate(
        market_data_worker=MarketDataWorker(data_path=csv_path),
        verification_loop=VerificationLoop(),
        trace_events=trace_events,
    )
    context_builder = ContextViewBuilder()

    user_text = "Tracey, load MBB daily data. This is home."
    interpreted = main_brain.interpret_request(user_text)

    context_view = context_builder.build_pre_action(
        live_state=state_manager.get_state(),
        task_focus="run market-data worker",
        current_environment_state=f"sample_csv_exists={csv_path.exists()}",
        last_verified_result=None,
        open_obligations=["execute worker", "verify", "synthesize"],
        current_risk="worker authority must remain bounded",
    )

    payload, verification_record = execution_gate.run_market_data_flow(
        ticker=interpreted["ticker"],
        timeframe="1D",
    )

    governance = governance_pass.run(
        context_view=context_view,
        live_state=state_manager.get_state().to_dict(),
        delta_log=state_manager.get_recent_deltas()[-1].to_dict(),
        current_message=user_text,
        draft_response="Done. The task is completed successfully.",
        action_status=verification_record.to_dict(),
        archive_status={"archive_consulted": False, "fragments_used": 0},
        task_type="execution",
        domain="build/research",
        action_phase="post_action",
        mode_confidence=0.90,
        risk_score=0.45,
        stakes_signal=0.75,
        memory_commit_possible=False,
        disagreement_likelihood=0.10,
        cue_strength=0.20,
        high_risk_domain=False,
        unanswerable_likelihood=0.05,
    )

    base_response = router.route(
        user_text,
        worker_payload=payload,
        verification_record=verification_record,
        render_mode="user",
        monitor_summary=governance["monitor_summary"],
    )

    tracey_result = tracey_runtime_pass.run(
        user_text=user_text,
        context_view=context_view,
        current_state=state_manager.get_state().to_dict(),
        base_response=base_response,
        monitor_summary=governance["monitor_summary"],
    )

    trace_events.log_tracey_turn(tracey_turn=tracey_result["tracey_turn"])
    trace_events.log_tracey_state_patch(state_patch=tracey_result["state_patch"])

    assert "Recognition note: home field may be active." in tracey_result["adapted_response"]
    assert tracey_result["state_patch"]["tracey_mode_hint"] == "home"

    categories = [event["category"] for event in logger.all_events()]
    assert "tracey_turn" in categories
    assert "tracey_state_patch" in categories
