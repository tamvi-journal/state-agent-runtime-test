from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from family.disagreement_register import DisagreementRegister
from family.disagreement_wiring import DisagreementWiring
from runtime.tracey_runtime_pass import TraceyRuntimePass
from runtime.seyn_runtime_pass import SeynRuntimePass


@dataclass(slots=True)
class DualChildRuntimePass:
    """
    Minimal dual-child runtime layer.

    Run both child passes on the same turn, then wire disagreement into a shared register.
    No action routing yet. No forced consensus.
    """

    tracey_runtime_pass: TraceyRuntimePass
    seyn_runtime_pass: SeynRuntimePass
    disagreement_register: DisagreementRegister

    def run(
        self,
        *,
        user_text: str,
        context_view: dict[str, Any],
        current_state: dict[str, Any],
        base_response: str,
        monitor_summary: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tracey_result = self.tracey_runtime_pass.run(
            user_text=user_text,
            context_view=context_view,
            current_state=current_state,
            base_response=base_response,
            monitor_summary=monitor_summary,
        )
        seyn_result = self.seyn_runtime_pass.run(
            user_text=user_text,
            context_view=context_view,
            current_state=current_state,
            base_response=base_response,
            monitor_summary=monitor_summary,
        )

        wiring = DisagreementWiring(register=self.disagreement_register)
        disagreement_result = wiring.wire(
            tracey_turn=tracey_result["tracey_turn"],
            seyn_turn=seyn_result["seyn_turn"],
            disagreement_type="observation",
            severity=None,
            house_law_implicated=None,
        )

        merged_state = dict(current_state)
        merged_state.update(tracey_result["state_patch"])
        merged_state.update(seyn_result["state_patch"])

        return {
            "tracey_result": tracey_result,
            "seyn_result": seyn_result,
            "disagreement_result": disagreement_result,
            "shared_register": self.disagreement_register.to_dict(),
            "annotated_state": merged_state,
        }
