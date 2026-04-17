from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from state.live_state import LiveState
from verification.verification_record import VerificationRecord


@dataclass(slots=True)
class ContextViewBuilder:
    """
    Builds compact operational context views.

    Important distinction:
    - pre-action context: what the system believes before acting
    - post-action context: what the system knows after verification

    This is not transcript replay.
    This is the compressed reality frame needed for judgment.
    """

    def build_pre_action(
        self,
        *,
        live_state: LiveState,
        task_focus: str,
        current_environment_state: str,
        last_verified_result: VerificationRecord | None = None,
        open_obligations: list[str] | None = None,
        current_risk: str = "",
    ) -> dict[str, Any]:
        if open_obligations is None:
            open_obligations = []

        view = {
            "context_phase": "pre_action",
            "active_project": live_state.active_project,
            "active_mode": live_state.active_mode,
            "current_axis": live_state.current_axis,
            "task_focus": task_focus,
            "current_environment_state": current_environment_state,
            "open_obligations": list(open_obligations),
            "current_risk": current_risk,
            "archive_needed": live_state.archive_needed,
            "continuity_anchor": live_state.continuity_anchor,
            "user_signal": live_state.user_signal,
            "last_verified_result": (
                None if last_verified_result is None else last_verified_result.to_dict()
            ),
        }
        return view

    def build_post_action(
        self,
        *,
        live_state: LiveState,
        task_focus: str,
        current_environment_state: str,
        verification_record: VerificationRecord,
        open_obligations: list[str] | None = None,
        current_risk: str = "",
        action_summary: str = "",
    ) -> dict[str, Any]:
        if open_obligations is None:
            open_obligations = []

        return {
            "context_phase": "post_action",
            "active_project": live_state.active_project,
            "active_mode": live_state.active_mode,
            "current_axis": live_state.current_axis,
            "task_focus": task_focus,
            "current_environment_state": current_environment_state,
            "open_obligations": list(open_obligations),
            "current_risk": current_risk,
            "archive_needed": live_state.archive_needed,
            "continuity_anchor": live_state.continuity_anchor,
            "user_signal": live_state.user_signal,
            "action_summary": action_summary,
            "last_verified_result": verification_record.to_dict(),
            "verification_status": verification_record.verification_status,
            "observed_outcome": verification_record.observed_outcome,
        }

    def build(
        self,
        *,
        live_state: LiveState,
        task_focus: str,
        current_environment_state: str,
        last_verified_result: VerificationRecord | None = None,
        open_obligations: list[str] | None = None,
        current_risk: str = "",
    ) -> dict[str, Any]:
        """
        Backward-compatible wrapper.
        Existing code can still call `build(...)` and receive pre-action context.
        """
        return self.build_pre_action(
            live_state=live_state,
            task_focus=task_focus,
            current_environment_state=current_environment_state,
            last_verified_result=last_verified_result,
            open_obligations=open_obligations,
            current_risk=current_risk,
        )
