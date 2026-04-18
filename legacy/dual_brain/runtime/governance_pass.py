from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from allocator.effort_allocator import EffortAllocator
from allocator.effort_schema import EffortInput
from monitor.monitor_layer import MonitorLayer
from monitor.mirror_bridge import MirrorBridge


@dataclass(slots=True)
class GovernancePass:
    """
    Small integration layer for Phase 2.6.

    Purpose:
    - run Monitor
    - reflect through Mirror Bridge
    - route through Effort Allocator
    - return one compact governance package for this turn

    This is not a replacement for main_brain.
    It is a governance-side bundle that main_brain/runtime can consult.
    """

    monitor_layer: MonitorLayer
    mirror_bridge: MirrorBridge
    effort_allocator: EffortAllocator

    def run(
        self,
        *,
        context_view: dict[str, Any],
        live_state: dict[str, Any],
        delta_log: dict[str, Any],
        current_message: str,
        draft_response: str,
        action_status: dict[str, Any],
        archive_status: dict[str, Any],
        task_type: str,
        domain: str = "generic",
        action_phase: str = "synthesis",
        mode_confidence: float = 1.0,
        risk_score: float = 0.0,
        stakes_signal: float = 0.0,
        memory_commit_possible: bool = False,
        disagreement_likelihood: float = 0.0,
        cue_strength: float = 0.0,
        high_risk_domain: bool = False,
        unanswerable_likelihood: float = 0.0,
    ) -> dict[str, Any]:
        monitor_output = self.monitor_layer.evaluate(
            context_view=context_view,
            live_state=live_state,
            delta_log=delta_log,
            current_message=current_message,
            draft_response=draft_response,
            action_status=action_status,
            archive_status=archive_status,
        )

        monitor_summary = self.mirror_bridge.reflect(
            monitor_output=monitor_output,
            active_mode=str(live_state.get("active_mode", "")),
            task_type=task_type,
            action_phase=action_phase,
        )

        annotated_state = self.mirror_bridge.annotate_state(
            state=live_state,
            monitor_summary=monitor_summary,
        )

        effort_input = EffortInput(
            task_type=task_type,
            domain=domain,
            active_mode=str(live_state.get("active_mode", "")),
            mode_confidence=mode_confidence,
            ambiguity_score=monitor_output.ambiguity_risk,
            risk_score=risk_score,
            stakes_signal=stakes_signal,
            action_required=self._infer_action_required(task_type=task_type, action_status=action_status),
            memory_commit_possible=memory_commit_possible,
            disagreement_likelihood=disagreement_likelihood,
            cue_strength=cue_strength,
            verification_gap_estimate=monitor_output.fake_progress_risk,
            high_risk_domain=high_risk_domain,
            unanswerable_likelihood=unanswerable_likelihood,
        )
        effort_decision = self.effort_allocator.route(effort_input)

        return {
            "monitor_output": monitor_output.to_dict(),
            "monitor_summary": monitor_summary["monitor_summary"],
            "annotated_state": annotated_state,
            "effort_input": effort_input.to_dict(),
            "effort_decision": effort_decision.to_dict(),
        }

    @staticmethod
    def _infer_action_required(*, task_type: str, action_status: dict[str, Any]) -> bool:
        if task_type in {"execution", "verify"}:
            return True

        verification_status = str(action_status.get("verification_status", "none")).lower()
        observed_outcome = str(action_status.get("observed_outcome", ""))

        if verification_status in {"pending", "unknown"} and observed_outcome == "":
            return True

        return False
