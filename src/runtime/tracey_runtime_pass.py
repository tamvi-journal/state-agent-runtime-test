from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tracey.tracey_adapter import TraceyAdapter


@dataclass(slots=True)
class TraceyRuntimePass:
    """
    Turn-level Tracey integration pass.

    It does three things:
    - inspect the turn through Tracey profile
    - lightly patch runtime state
    - optionally adapt the outward response
    """

    adapter: TraceyAdapter

    def run(
        self,
        *,
        user_text: str,
        context_view: dict[str, Any],
        current_state: dict[str, Any],
        base_response: str,
        monitor_summary: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tracey_turn = self.adapter.inspect_turn(
            user_text=user_text,
            context_view=context_view,
            monitor_summary=monitor_summary,
        )
        state_patch = self.adapter.runtime_state_patch(tracey_turn=tracey_turn)
        adapted_response = self.adapter.adapt_response(
            base_response=base_response,
            tracey_turn=tracey_turn,
        )

        merged_state = dict(current_state)
        merged_state.update(state_patch)

        return {
            "tracey_turn": tracey_turn,
            "state_patch": state_patch,
            "annotated_state": merged_state,
            "adapted_response": adapted_response,
        }
