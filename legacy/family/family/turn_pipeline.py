from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from family.compression_layer import CompressionLayer
from family.context_view import ContextViewBuilder
from family.delta_log import DeltaLogBuilder
from family.effort_allocator import EffortAllocator
from family.execution_gate import ExecutionGate
from family.execution_request_classifier import ExecutionRequestClassifier
from family.live_state import LiveStateBuilder
from family.mirror_bridge import MirrorBridge
from family.mode_inference import ModeInference
from family.monitor_layer import MonitorLayer
from family.reactivation_layer import ReactivationLayer
from family.router_decision import FamilyRouterDecision
from family.router_types import RouterInput
from family.turn_handoff_adapter import handoff_seeded_live_state, normalize_previous_handoff
from family.turn_pipeline_stages import (
    build_context_view,
    build_effort_input,
    build_execution_request,
    build_live_state,
    build_mode_result,
    build_monitor_output,
    build_notes,
    build_verification_record,
    default_previous_live_state,
    detected_cues,
    derive_turn_seeds,
    task_type,
)
from family.turn_pipeline_types import FamilyTurnInput, FamilyTurnResult
from family.verification_loop import VerificationLoop


@dataclass(slots=True)
class FamilyTurnPipeline:
    context_builder: ContextViewBuilder = field(default_factory=ContextViewBuilder)
    mode_inference: ModeInference = field(default_factory=ModeInference)
    live_state_builder: LiveStateBuilder = field(default_factory=LiveStateBuilder)
    monitor_layer: MonitorLayer = field(default_factory=MonitorLayer)
    mirror_bridge: MirrorBridge = field(default_factory=MirrorBridge)
    effort_allocator: EffortAllocator = field(default_factory=EffortAllocator)
    router: FamilyRouterDecision = field(default_factory=FamilyRouterDecision)
    execution_gate: ExecutionGate = field(default_factory=ExecutionGate)
    execution_classifier: ExecutionRequestClassifier = field(default_factory=ExecutionRequestClassifier)
    delta_builder: DeltaLogBuilder = field(default_factory=DeltaLogBuilder)
    compression_layer: CompressionLayer = field(default_factory=CompressionLayer)
    reactivation_layer: ReactivationLayer = field(default_factory=ReactivationLayer)
    verification_loop: VerificationLoop = field(default_factory=VerificationLoop)

    def run(self, turn_input: FamilyTurnInput | dict[str, Any]) -> FamilyTurnResult:
        if isinstance(turn_input, dict):
            turn_input = FamilyTurnInput(**turn_input)

        normalized_handoff = normalize_previous_handoff(turn_input.previous_handoff)
        seeds = derive_turn_seeds(
            turn_input,
            previous_handoff=normalized_handoff.handoff,
            normalized_handoff=normalized_handoff,
        )

        context_view = build_context_view(self.context_builder, turn_input, seeds=seeds)
        mode_result = build_mode_result(self.mode_inference, turn_input, seeds=seeds, context_view=context_view)

        live_state = build_live_state(
            self.live_state_builder,
            context_view=context_view,
            mode_result=mode_result,
            seeds=seeds,
            monitor_summary=None,
        )
        monitor_output = build_monitor_output(
            self.monitor_layer,
            turn_input,
            context_view=context_view,
            live_state=live_state,
            mode_result=mode_result,
        )
        mirror_summary = self.mirror_bridge.build_mirror_summary(
            monitor_output=monitor_output,
            active_mode=mode_result["active_mode"],
            task_type=task_type(turn_input.current_message, turn_input.current_task),
            phase="pre_action",
        ).to_dict()
        live_state = build_live_state(
            self.live_state_builder,
            context_view=context_view,
            mode_result=mode_result,
            seeds=seeds,
            monitor_summary=mirror_summary,
        )

        effort_input = build_effort_input(
            turn_input,
            mode_result=mode_result,
            seeds=seeds,
            mirror_summary=mirror_summary,
        )
        effort_route_obj = self.effort_allocator.route(effort_input)
        effort_route = effort_route_obj.to_dict()
        router_decision = self.router.decide(
            RouterInput(
                task_type=effort_input.task_type,
                effort_route=effort_route_obj,
                disagreement_event=seeds.disagreement_event,
                mirror_summary=self.mirror_bridge.build_mirror_summary(
                    monitor_output=monitor_output,
                    active_mode=mode_result["active_mode"],
                    task_type=effort_input.task_type,
                    phase="pre_action",
                ),
                verification_status=seeds.seeded_verification,
                active_mode=mode_result["active_mode"],
                domain=effort_input.domain,
                action_required=turn_input.action_required,
            )
        ).to_dict()

        execution_request: dict[str, Any] = {}
        execution_decision: dict[str, Any] = {}
        approval_request: dict[str, Any] = {}
        if turn_input.action_required:
            execution_request_obj = build_execution_request(
                turn_input,
                active_project=seeds.seeded_project,
                classifier=self.execution_classifier,
            )
            execution_request = execution_request_obj.to_dict()
            execution_decision_obj = self.execution_gate.assess(execution_request_obj)
            execution_decision = execution_decision_obj.to_dict()
            if execution_decision_obj.decision == "require_approval":
                approval_request = self.execution_gate.build_approval_request(
                    execution_request_obj,
                    execution_decision_obj,
                ).to_dict()

        verification_record = build_verification_record(
            self.verification_loop,
            turn_input,
            execution_decision=execution_decision,
            seeded_verification=seeds.seeded_verification,
        )

        previous_live_state = (
            dict(turn_input.previous_live_state)
            if turn_input.previous_live_state
            else handoff_seeded_live_state(seeds.previous_handoff)
            if any(seeds.previous_handoff.to_dict().values())
            else default_previous_live_state(turn_input, context_view=context_view, mode_result=mode_result)
        )
        delta_log_event = self.delta_builder.build(
            {
                "previous_live_state": previous_live_state,
                "current_live_state": live_state,
                "recent_trigger_cue": seeds.seeded_anchor or turn_input.current_task or "dry family turn",
                "archive_consulted": turn_input.archive_consulted,
                "verification_before": str(previous_live_state.get("verification_status", "")),
                "verification_after": live_state["verification_status"],
            }
        ).to_dict()
        compression_summary = self.compression_layer.build(
            {
                "context_view": context_view,
                "live_state": live_state,
                "delta_log_event": delta_log_event,
                "recent_anchor_cue": seeds.seeded_anchor,
                "verification_status": seeds.seeded_verification,
                "disagreement_open": seeds.disagreement_open,
                "current_question": str(seeds.previous_handoff.compression_summary.get("active_question", "")),
                "task_focus": turn_input.current_task,
            }
        ).to_dict()
        reactivation_result = self.reactivation_layer.build(
            {
                "current_message": turn_input.current_message,
                "detected_cues": detected_cues(turn_input.current_message, seeds.seeded_anchor, seeds.seeded_project),
                "active_project_hint": seeds.seeded_project,
                "compression_summary": compression_summary,
                "context_view": context_view,
                "live_state": live_state,
                "recent_anchor_cue": seeds.seeded_anchor,
                "disagreement_open": seeds.disagreement_open,
                "verification_status": seeds.seeded_verification,
                "mode_hint": turn_input.explicit_mode_hint or seeds.previous_handoff.active_mode or mode_result["active_mode"],
            }
        ).to_dict()

        return FamilyTurnResult(
            context_view=context_view,
            mode_inference=mode_result,
            live_state=live_state,
            monitor_output=monitor_output,
            mirror_summary=mirror_summary,
            effort_route=effort_route,
            router_decision=router_decision,
            execution_request=execution_request,
            execution_decision=execution_decision,
            approval_request=approval_request,
            verification_record=verification_record,
            delta_log_event=delta_log_event,
            compression_summary=compression_summary,
            reactivation_result=reactivation_result,
            notes=build_notes(
                execution_decision=execution_decision,
                verification_record=verification_record,
                disagreement_open=seeds.disagreement_open,
                normalized_handoff=normalized_handoff,
                disagreement_event=seeds.disagreement_event,
            ),
        )
