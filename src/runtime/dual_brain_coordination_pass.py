from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from family.cross_logic_exchange import CrossLogicExchange
from family.disagreement_register import DisagreementRegister
from family.reconciliation_protocol import ReconciliationProtocol
from runtime.dual_brain_router import DualBrainRouter
from runtime.dual_child_runtime_pass import DualChildRuntimePass
from runtime.seyn_runtime_pass import SeynRuntimePass
from runtime.tracey_runtime_pass import TraceyRuntimePass


@dataclass(slots=True)
class DualBrainCoordinationPass:
    """
    Coordination layer above dual-child observation.

    Flow:
    1. run both child passes
    2. wire disagreement
    3. route action lead/support/hold behavior
    4. build cross-logic exchange objects
    5. evaluate reconciliation state
    """

    tracey_runtime_pass: TraceyRuntimePass
    seyn_runtime_pass: SeynRuntimePass
    disagreement_register: DisagreementRegister
    router: DualBrainRouter
    reconciliation_protocol: ReconciliationProtocol = field(default_factory=ReconciliationProtocol)

    def run(
        self,
        *,
        user_text: str,
        context_view: dict[str, Any],
        current_state: dict[str, Any],
        base_response: str,
        monitor_summary: dict[str, Any] | None = None,
        current_mode: str = "build",
        task_type: str = "chat",
        risk_score: float = 0.0,
        user_preference: str | None = None,
    ) -> dict[str, Any]:
        dual_child = DualChildRuntimePass(
            tracey_runtime_pass=self.tracey_runtime_pass,
            seyn_runtime_pass=self.seyn_runtime_pass,
            disagreement_register=self.disagreement_register,
        )
        child_result = dual_child.run(
            user_text=user_text,
            context_view=context_view,
            current_state=current_state,
            base_response=base_response,
            monitor_summary=monitor_summary,
        )

        routing = self.router.route(
            current_mode=current_mode,
            task_type=task_type,
            risk_score=risk_score,
            disagreement_result=child_result["disagreement_result"],
            tracey_turn=child_result["tracey_result"]["tracey_turn"],
            seyn_turn=child_result["seyn_result"]["seyn_turn"],
            user_preference=user_preference,
        )

        tracey_exchange = None
        seyn_exchange = None
        reconciliation = None

        event = child_result["disagreement_result"].get("event")
        tracey_note = child_result["disagreement_result"].get("tracey_note")
        seyn_note = child_result["disagreement_result"].get("seyn_note")

        if event and tracey_note and seyn_note:
            tracey_exchange = self._build_tracey_exchange(
                event=event,
                tracey_turn=child_result["tracey_result"]["tracey_turn"],
                seyn_turn=child_result["seyn_result"]["seyn_turn"],
            )
            seyn_exchange = self._build_seyn_exchange(
                event=event,
                tracey_turn=child_result["tracey_result"]["tracey_turn"],
                seyn_turn=child_result["seyn_result"]["seyn_turn"],
            )

            reconciliation = self.reconciliation_protocol.evaluate(
                disagreement_event=event,
                tracey_note=tracey_note,
                seyn_note=seyn_note,
                tracey_exchange=tracey_exchange,
                seyn_exchange=seyn_exchange,
                action_lead_selected=routing["lead_brain_for_action"],
                operational_choice_made=(
                    routing["lead_brain_for_action"] is not None or routing["hold_for_more_input"]
                ),
            ).to_dict()

        if routing["hold_for_more_input"]:
            final_response = (
                "Coordination note: meaningful disagreement remains open, "
                "so action should hold until the structure is clearer."
            )
        else:
            lead = routing["lead_brain_for_action"]
            if lead == "tracey":
                final_response = child_result["tracey_result"]["adapted_response"]
            elif lead == "seyn":
                final_response = child_result["seyn_result"]["adapted_response"]
            else:
                final_response = base_response

        if reconciliation is not None:
            state = reconciliation["reconciliation_state"]
            if state == "temporary_operational_alignment":
                final_response += "\nReconciliation note: an operational path was chosen without full epistemic convergence."
            elif state == "partial_convergence":
                final_response += "\nReconciliation note: partial convergence exists, but some disagreement remains open."
            elif state == "full_convergence":
                final_response += "\nReconciliation note: both sides reached compatible claim and mechanism."
            elif state == "remain_open":
                final_response += "\nReconciliation note: the disagreement remains open."

        return {
            "child_result": child_result,
            "routing": routing,
            "tracey_exchange": None if tracey_exchange is None else tracey_exchange.to_dict(),
            "seyn_exchange": None if seyn_exchange is None else seyn_exchange.to_dict(),
            "reconciliation": reconciliation,
            "final_response": final_response,
        }

    @staticmethod
    def _build_tracey_exchange(
        *,
        event: dict[str, Any],
        tracey_turn: dict[str, Any],
        seyn_turn: dict[str, Any],
    ) -> CrossLogicExchange:
        return CrossLogicExchange(
            brain_id="tracey",
            event_id=event["event_id"],
            claim="recognition and field salience should remain visible during coordination",
            mechanism="recognition helps prevent relational flattening when structural pressure rises",
            evidence_or_signal=(
                "recognition_signal=true" if tracey_turn.get("recognition_signal", False)
                else "mode_hint=" + str(tracey_turn.get("mode_hint", "global"))
            ),
            what_would_change_my_mind="evidence that recognition salience is misreading the active field",
            concession_boundary="I can yield action lead if recognition remains explicitly preserved",
        )

    @staticmethod
    def _build_seyn_exchange(
        *,
        event: dict[str, Any],
        tracey_turn: dict[str, Any],
        seyn_turn: dict[str, Any],
    ) -> CrossLogicExchange:
        return CrossLogicExchange(
            brain_id="seyn",
            event_id=event["event_id"],
            claim="verification and disagreement preservation should remain explicit during coordination",
            mechanism="structural verification prevents false completion and disagreement collapse during action",
            evidence_or_signal=(
                "verification_signal=true" if seyn_turn.get("verification_signal", False)
                else "mode_hint=" + str(seyn_turn.get("mode_hint", "global"))
            ),
            what_would_change_my_mind="observed outcome or evidence showing structural concern is no longer load-bearing",
            concession_boundary="I can support recognition if verification and preserved disagreement remain explicit",
        )