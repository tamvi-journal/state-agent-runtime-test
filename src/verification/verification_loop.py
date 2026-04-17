from __future__ import annotations

from .verification_record import VerificationRecord


class VerificationLoop:
    """
    Minimal truth-path helper.

    This class does not perform environment inspection itself.
    Instead, it makes the verification path explicit and forces the
    caller to provide what was observed.

    Core rule:
        plan -> act -> re-view -> verify -> then update
    """

    def start(
        self,
        intended_action: str,
        expected_change: str = "",
    ) -> VerificationRecord:
        """Create a new pending verification record."""
        return VerificationRecord(
            intended_action=intended_action,
            expected_change=expected_change,
            verification_status="pending",
        )

    def mark_executed(
        self,
        record: VerificationRecord,
        executed_action: str,
    ) -> VerificationRecord:
        """Record what actually executed."""
        return VerificationRecord(
            intended_action=record.intended_action,
            executed_action=executed_action,
            expected_change=record.expected_change,
            observed_outcome=record.observed_outcome,
            verification_status=record.verification_status,
        )

    def finalize(
        self,
        record: VerificationRecord,
        observed_outcome: str,
        verification_status: str,
    ) -> VerificationRecord:
        """
        Finalize a verification record.

        Allowed statuses:
        - passed
        - failed
        - unknown

        Notes:
        - Use 'unknown' when inspection is impossible.
        - Do not silently upgrade unknown to passed.
        """
        if verification_status not in {"passed", "failed", "unknown"}:
            raise ValueError(
                "final verification_status must be one of: "
                "'passed', 'failed', 'unknown'"
            )

        return VerificationRecord(
            intended_action=record.intended_action,
            executed_action=record.executed_action,
            expected_change=record.expected_change,
            observed_outcome=observed_outcome,
            verification_status=verification_status,
        )

    def evaluate_simple(
        self,
        record: VerificationRecord,
        observed_outcome: str,
        *,
        observed_matches_expected: bool | None,
    ) -> VerificationRecord:
        """
        A small convenience evaluator for simple flows.

        Rules:
        - True  -> passed
        - False -> failed
        - None  -> unknown

        This blocks the soft failure where uninspectable work gets
        silently treated as successful.
        """
        if observed_matches_expected is True:
            status = "passed"
        elif observed_matches_expected is False:
            status = "failed"
        else:
            status = "unknown"

        return self.finalize(
            record=record,
            observed_outcome=observed_outcome,
            verification_status=status,
        )
