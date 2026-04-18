from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

from allocator.effort_allocator import EffortAllocator
from context.context_view import ContextViewBuilder
from core.main_brain import MainBrain
from family.disagreement_register import DisagreementRegister
from family.reconciliation_protocol import ReconciliationProtocol
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


@dataclass(slots=True)
class RuntimeProvider:
    """
    Runtime-chain-backed provider for local app usage.

    Prefers configurable sample data path so local runs are stable across environments.
    """

    sample_data_path: str = ""

    def resolved_sample_data_path(self) -> str:
        explicit = self.sample_data_path.strip()
        if explicit:
            return explicit
        env_path = os.getenv("SAMPLE_DATA_PATH", "").strip()
        if env_path:
            return env_path
        return "data/sample_market_data.csv"

    def get_runtime_result(self, *, user_text: str = "hello there") -> dict[str, Any]:
        sample_data_path = self.resolved_sample_data_path()

        live_state = LiveState(
            active_mode="build",
            current_axis="technical",
            coherence_level=0.92,
            tension_flags=[],
            active_project="state-memory-agent",
            user_signal="local app runtime provider",
            continuity_anchor="fastapi-local-runtime",
            archive_needed=False,
        )
        state_manager = StateManager(live_state=live_state)
        state_manager.append_delta(
            DeltaRecord(
                mode_shift="",
                coherence_shift=0.0,
                policy_intrusion_detected=False,
                repair_event=False,
                trigger_cue="runtime_provider_start",
                archive_consulted=False,
            )
        )

        main_brain = MainBrain(state_manager=state_manager)
        router = RequestRouter(main_brain=main_brain)
        context_builder = ContextViewBuilder()
        governance_pass = GovernancePass(
            monitor_layer=MonitorLayer(),
            mirror_bridge=MirrorBridge(),
            effort_allocator=EffortAllocator(),
        )

        worker = MarketDataWorker(data_path=sample_data_path)
        logger = EventLogger()
        trace_events = TraceEvents(logger=logger)
        execution_gate = ExecutionGate(
            market_data_worker=worker,
            verification_loop=VerificationLoop(),
            trace_events=trace_events,
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
            reconciliation_protocol=ReconciliationProtocol(),
        )

        interpreted = main_brain.interpret_request(user_text)
        context_view = context_builder.build_pre_action(
            live_state=state_manager.get_state(),
            task_focus="run local runtime provider path",
            current_environment_state=f"sample_data_path={sample_data_path}",
            last_verified_result=None,
            open_obligations=["interpret", "govern", "coordinate", "synthesize"],
            current_risk="keep local runtime path bounded",
        )

        governance_output = governance_pass.run(
            context_view=context_view,
            live_state=state_manager.get_state().to_dict(),
            delta_log=state_manager.get_recent_deltas()[-1].to_dict(),
            current_message=user_text,
            draft_response="Preparing bounded runtime response.",
            action_status={"verification_status": "pending", "observed_outcome": ""},
            archive_status={"archive_consulted": False, "fragments_used": 0},
            task_type="execution" if interpreted.get("needs_worker") else "chat",
            domain="build/research",
            action_phase="pre_action",
            mode_confidence=0.90,
            risk_score=0.55,
            stakes_signal=0.70,
            memory_commit_possible=False,
            disagreement_likelihood=0.30,
            cue_strength=0.30,
            high_risk_domain=False,
            unanswerable_likelihood=0.10,
        )

        verification_record = None
        worker_payload = None

        if interpreted.get("needs_worker") and interpreted.get("ticker"):
            worker_payload, verification_record = execution_gate.run_market_data_flow(
                ticker=interpreted["ticker"],
                timeframe="1D",
            )
            base_response = router.route(
                user_text,
                worker_payload=worker_payload,
                verification_record=verification_record,
                render_mode="user",
                monitor_summary=governance_output["monitor_summary"],
            )
            task_type = "execution"
            risk_score = 0.80
        else:
            base_response = router.route(
                user_text,
                render_mode="user",
                monitor_summary=governance_output["monitor_summary"],
            )
            task_type = "chat"
            risk_score = 0.20

        coordination = coordination_pass.run(
            user_text=user_text,
            context_view=context_view,
            current_state=state_manager.get_state().to_dict(),
            base_response=base_response,
            monitor_summary=governance_output["monitor_summary"],
            current_mode=state_manager.get_state().active_mode,
            task_type=task_type,
            risk_score=risk_score,
            user_preference=None,
        )

        return {
            "final_response": coordination["final_response"],
            "routing": coordination["routing"],
            "reconciliation": coordination["reconciliation"],
            "child_result": coordination["child_result"],
            "tracey_exchange": coordination["tracey_exchange"],
            "seyn_exchange": coordination["seyn_exchange"],
            "context_view": context_view,
            "governance_output": governance_output,
            "worker_payload": worker_payload,
            "verification_record": None if verification_record is None else verification_record.to_dict(),
            "base_response": base_response,
            "user_text": user_text,
            "sample_data_path": sample_data_path,
        }
