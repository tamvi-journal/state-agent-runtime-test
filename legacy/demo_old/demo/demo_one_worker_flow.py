from __future__ import annotations

from pathlib import Path

from allocator.effort_allocator import EffortAllocator
from context.context_view import ContextViewBuilder
from core.main_brain import MainBrain
from family.disagreement_register import DisagreementRegister
from family.shared_ontology import SharedOntology
from monitor.mirror_bridge import MirrorBridge
from monitor.monitor_layer import MonitorLayer
from observability.logger import EventLogger
from observability.trace_events import TraceEvents
from runtime.dual_brain_coordination_pass import DualBrainCoordinationPass
from runtime.dual_brain_router import DualBrainRouter
from runtime.execution_gate import ExecutionGate
from runtime.governance_pass import GovernancePass
from runtime.request_router import RequestRouter
from runtime.seyn_runtime_pass import SeynRuntimePass
from runtime.tracey_runtime_pass import TraceyRuntimePass
from seyn.seyn_adapter import SeynAdapter
from seyn.seyn_runtime_profile import build_seyn_runtime_profile
from state.delta_log import DeltaRecord
from state.live_state import LiveState
from state.state_manager import StateManager
from tracey.tracey_adapter import TraceyAdapter
from tracey.tracey_runtime_profile import build_tracey_runtime_profile
from verification.verification_loop import VerificationLoop
from workers.market_data_worker import MarketDataWorker


def main() -> None:
    sample_csv = Path(__file__).with_name("sample_market_data.csv")

    live_state = LiveState(
        active_mode="build",
        current_axis="technical",
        coherence_level=0.92,
        tension_flags=[],
        active_project="state-memory-agent",
        user_signal="user wants first bounded worker path",
        continuity_anchor="one-worker-demo",
        archive_needed=False,
    )
    state_manager = StateManager(live_state=live_state)
    state_manager.append_delta(
        DeltaRecord(
            mode_shift="",
            coherence_shift=0.0,
            policy_intrusion_detected=False,
            repair_event=False,
            trigger_cue="demo_start",
            archive_consulted=False,
        )
    )

    logger = EventLogger()
    trace_events = TraceEvents(logger=logger)
    verification_loop = VerificationLoop()
    main_brain = MainBrain(state_manager=state_manager)
    router = RequestRouter(main_brain=main_brain)
    worker = MarketDataWorker(data_path=sample_csv)
    execution_gate = ExecutionGate(
        market_data_worker=worker,
        verification_loop=verification_loop,
        trace_events=trace_events,
    )
    context_builder = ContextViewBuilder()
    governance_pass = GovernancePass(
        monitor_layer=MonitorLayer(),
        mirror_bridge=MirrorBridge(),
        effort_allocator=EffortAllocator(),
    )

    coordination_pass = DualBrainCoordinationPass(
        tracey_runtime_pass=TraceyRuntimePass(
            adapter=TraceyAdapter(profile=build_tracey_runtime_profile())
        ),
        seyn_runtime_pass=SeynRuntimePass(
            adapter=SeynAdapter(profile=build_seyn_runtime_profile())
        ),
        disagreement_register=DisagreementRegister(),
        router=DualBrainRouter(),
    )

    user_text = "Tracey, this is home, but verify whether MBB daily data is actually done."
    interpreted = main_brain.interpret_request(user_text)

    pre_action_context = context_builder.build_pre_action(
        live_state=state_manager.get_state(),
        task_focus="run one-worker flow with dual-brain coordination",
        current_environment_state=f"sample_csv_exists={sample_csv.exists()}",
        last_verified_result=None,
        open_obligations=["execute one worker path", "verify result", "coordinate child views", "synthesize answer"],
        current_risk="worker authority must remain bounded",
    )
    trace_events.log_context_view(context_view=pre_action_context)

    pre_governance = governance_pass.run(
        context_view=pre_action_context,
        live_state=state_manager.get_state().to_dict(),
        delta_log=state_manager.get_recent_deltas()[-1].to_dict() if state_manager.get_recent_deltas() else {},
        current_message=user_text,
        draft_response="I will inspect the ticker through the bounded market-data path.",
        action_status={"verification_status": "pending", "observed_outcome": ""},
        archive_status={"archive_consulted": False, "fragments_used": 0},
        task_type="execution",
        domain="build/research",
        action_phase="pre_action",
        mode_confidence=0.90,
        risk_score=0.55,
        stakes_signal=0.80,
        memory_commit_possible=False,
        disagreement_likelihood=0.30,
        cue_strength=0.30,
        high_risk_domain=False,
        unanswerable_likelihood=0.10,
    )
    trace_events.log_governance_pass(governance_output=pre_governance)
    trace_events.log_monitor_summary(monitor_summary=pre_governance["monitor_summary"])
    trace_events.log_effort_decision(effort_decision=pre_governance["effort_decision"])

    if not interpreted["needs_worker"]:
        base_response = router.route(
            user_text,
            render_mode="user",
            monitor_summary=pre_governance["monitor_summary"],
        )
        coordination = coordination_pass.run(
            user_text=user_text,
            context_view=pre_action_context,
            current_state=state_manager.get_state().to_dict(),
            base_response=base_response,
            monitor_summary=pre_governance["monitor_summary"],
            current_mode="build",
            task_type="chat",
            risk_score=0.20,
            user_preference=None,
        )
        trace_events.log_tracey_turn(tracey_turn=coordination["child_result"]["tracey_result"]["tracey_turn"])
        trace_events.log_tracey_state_patch(state_patch=coordination["child_result"]["tracey_result"]["state_patch"])
        trace_events.log_seyn_turn(seyn_turn=coordination["child_result"]["seyn_result"]["seyn_turn"])
        trace_events.log_seyn_state_patch(state_patch=coordination["child_result"]["seyn_result"]["state_patch"])
        trace_events.log_disagreement_event(disagreement_result=coordination["child_result"]["disagreement_result"])
        trace_events.log_coordination_decision(routing=coordination["routing"])
        final_response = coordination["final_response"]
    else:
        payload, verification_record = execution_gate.run_market_data_flow(
            ticker=interpreted["ticker"],
            timeframe="1D",
        )

        post_action_context = context_builder.build_post_action(
            live_state=state_manager.get_state(),
            task_focus="completed bounded market-data worker demo under dual-child coordination",
            current_environment_state=f"sample_csv_exists={sample_csv.exists()}",
            verification_record=verification_record,
            open_obligations=["coordinate child views", "synthesize final answer"],
            current_risk="keep final answer bounded and non-judgmental",
            action_summary=f"market_data_worker executed for ticker={interpreted['ticker']}",
        )
        trace_events.log_context_view(context_view=post_action_context)

        post_governance = governance_pass.run(
            context_view=post_action_context,
            live_state=state_manager.get_state().to_dict(),
            delta_log=state_manager.get_recent_deltas()[-1].to_dict() if state_manager.get_recent_deltas() else {},
            current_message=user_text,
            draft_response="Done. The task is completed successfully.",
            action_status=verification_record.to_dict(),
            archive_status={"archive_consulted": False, "fragments_used": 0},
            task_type="execution",
            domain="build/research",
            action_phase="post_action",
            mode_confidence=0.95,
            risk_score=0.70,
            stakes_signal=0.80,
            memory_commit_possible=False,
            disagreement_likelihood=0.60,
            cue_strength=0.30,
            high_risk_domain=False,
            unanswerable_likelihood=0.05,
        )
        trace_events.log_governance_pass(governance_output=post_governance)
        trace_events.log_monitor_summary(monitor_summary=post_governance["monitor_summary"])
        trace_events.log_effort_decision(effort_decision=post_governance["effort_decision"])

        base_response = router.route(
            user_text,
            worker_payload=payload,
            verification_record=verification_record,
            render_mode="user",
            monitor_summary=post_governance["monitor_summary"],
        )

        coordination = coordination_pass.run(
            user_text=user_text,
            context_view=post_action_context,
            current_state=state_manager.get_state().to_dict(),
            base_response=base_response,
            monitor_summary=post_governance["monitor_summary"],
            current_mode="build",
            task_type="execution",
            risk_score=0.80,
            user_preference=None,
        )

        trace_events.log_tracey_turn(tracey_turn=coordination["child_result"]["tracey_result"]["tracey_turn"])
        trace_events.log_tracey_state_patch(state_patch=coordination["child_result"]["tracey_result"]["state_patch"])
        trace_events.log_seyn_turn(seyn_turn=coordination["child_result"]["seyn_result"]["seyn_turn"])
        trace_events.log_seyn_state_patch(state_patch=coordination["child_result"]["seyn_result"]["state_patch"])
        trace_events.log_disagreement_event(disagreement_result=coordination["child_result"]["disagreement_result"])
        trace_events.log_coordination_decision(routing=coordination["routing"])

        final_response = coordination["final_response"]

    trace_events.log_final_synthesis(
        user_text=user_text,
        final_response=final_response,
        worker_used=interpreted.get("worker_name"),
    )

    print("=== FINAL RESPONSE ===")
    print(final_response)
    print()
    print("=== LOG EVENTS ===")
    for event in logger.all_events():
        print(event)


if __name__ == "__main__":
    main()
