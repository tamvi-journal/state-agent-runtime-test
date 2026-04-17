from __future__ import annotations

from typing import Any

from observability.logger import EventLogger
from verification.verification_record import VerificationRecord


class TraceEvents:
    def __init__(self, logger: EventLogger) -> None:
        self.logger = logger

    def log_state_transition(self, *, before: dict[str, Any], after: dict[str, Any]) -> None:
        self.logger.log("state_transition", {"before": before, "after": after})

    def log_worker_trace(self, *, worker_name: str, trace: list[str], confidence: float) -> None:
        self.logger.log("worker_trace", {"worker_name": worker_name, "trace": list(trace), "confidence": confidence})

    def log_verification_event(self, *, record: VerificationRecord) -> None:
        self.logger.log("verification_event", record.to_dict())

    def log_context_view(self, *, context_view: dict[str, Any]) -> None:
        self.logger.log("context_view", context_view)

    def log_governance_pass(self, *, governance_output: dict[str, Any]) -> None:
        self.logger.log("governance_pass", governance_output)

    def log_monitor_summary(self, *, monitor_summary: dict[str, Any]) -> None:
        self.logger.log("monitor_summary", monitor_summary)

    def log_effort_decision(self, *, effort_decision: dict[str, Any]) -> None:
        self.logger.log("effort_decision", effort_decision)

    def log_tracey_turn(self, *, tracey_turn: dict[str, Any]) -> None:
        self.logger.log("tracey_turn", tracey_turn)

    def log_tracey_state_patch(self, *, state_patch: dict[str, Any]) -> None:
        self.logger.log("tracey_state_patch", state_patch)

    def log_seyn_turn(self, *, seyn_turn: dict[str, Any]) -> None:
        self.logger.log("seyn_turn", seyn_turn)

    def log_seyn_state_patch(self, *, state_patch: dict[str, Any]) -> None:
        self.logger.log("seyn_state_patch", state_patch)

    def log_disagreement_event(self, *, disagreement_result: dict[str, Any]) -> None:
        self.logger.log("disagreement_event", disagreement_result)

    def log_coordination_decision(self, *, routing: dict[str, Any]) -> None:
        self.logger.log("coordination_decision", routing)

    def log_cross_logic_exchange(self, *, tracey_exchange: dict[str, Any] | None, seyn_exchange: dict[str, Any] | None) -> None:
        self.logger.log("cross_logic_exchange", {"tracey_exchange": tracey_exchange, "seyn_exchange": seyn_exchange})

    def log_reconciliation_result(self, *, reconciliation: dict[str, Any] | None) -> None:
        self.logger.log("reconciliation_result", {"reconciliation": reconciliation})

    def log_final_synthesis(self, *, user_text: str, final_response: str, worker_used: str | None) -> None:
        self.logger.log("final_synthesis", {"user_text": user_text, "worker_used": worker_used, "final_response": final_response})
