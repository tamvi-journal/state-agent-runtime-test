from __future__ import annotations

from verification.verification_loop import VerificationLoop


def test_verification_loop_marks_passed_when_observation_matches() -> None:
    loop = VerificationLoop()

    record = loop.start(
        intended_action="run market_data_worker for MBB",
        expected_change="bounded market-data payload should exist for ticker=MBB",
    )
    record = loop.mark_executed(
        record,
        executed_action="market_data_worker.run(ticker=MBB, timeframe=1D)",
    )
    record = loop.evaluate_simple(
        record,
        observed_outcome="worker returned bars_found=3 for ticker=MBB",
        observed_matches_expected=True,
    )

    assert record.verification_status == "passed"


def test_verification_loop_marks_failed_when_observation_does_not_match() -> None:
    loop = VerificationLoop()

    record = loop.start(
        intended_action="run market_data_worker for MBB",
        expected_change="bounded market-data payload should exist for ticker=MBB",
    )
    record = loop.mark_executed(
        record,
        executed_action="market_data_worker.run(ticker=MBB, timeframe=1D)",
    )
    record = loop.evaluate_simple(
        record,
        observed_outcome="worker returned bars_found=0 for ticker=MBB",
        observed_matches_expected=False,
    )

    assert record.verification_status == "failed"


def test_verification_loop_marks_unknown_when_match_is_unknown() -> None:
    loop = VerificationLoop()

    record = loop.start(
        intended_action="inspect external side effect",
        expected_change="external state may change",
    )
    record = loop.mark_executed(
        record,
        executed_action="some external action",
    )
    record = loop.evaluate_simple(
        record,
        observed_outcome="external system could not be inspected",
        observed_matches_expected=None,
    )

    assert record.verification_status == "unknown"
