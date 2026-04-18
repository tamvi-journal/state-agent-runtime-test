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

    def log_final_synthesis(self, *, user_text: str, final_response: str, worker_used: str | None) -> None:
        self.logger.log("final_synthesis", {"user_text": user_text, "worker_used": worker_used, "final_response": final_response})
