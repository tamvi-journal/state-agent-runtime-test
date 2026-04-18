from __future__ import annotations

from verification.verification_loop import VerificationLoop


def test_start_creates_pending_record() -> None:
    loop = VerificationLoop()
    record = loop.start(
        intended_action="run market_data_worker",
        expected_change="bounded payload should exist",
    )

    assert record.verification_status == "pending"
    assert record.executed_action == ""


def test_mark_executed_keeps_intent_and_records_execution() -> None:
    loop = VerificationLoop()
    record = loop.mark_executed(
        loop.start(
            intended_action="run market_data_worker",
            expected_change="bounded payload should exist",
        ),
        executed_action="market_data_worker.run(ticker=MBB, timeframe=1D)",
    )

    assert record.executed_action == "market_data_worker.run(ticker=MBB, timeframe=1D)"
    assert record.verification_status == "pending"


def test_evaluate_simple_true_yields_passed() -> None:
    loop = VerificationLoop()
    record = loop.evaluate_simple(
        loop.mark_executed(
            loop.start(
                intended_action="run market_data_worker",
                expected_change="bounded payload should exist",
            ),
            executed_action="market_data_worker.run(ticker=MBB, timeframe=1D)",
        ),
        observed_outcome="worker returned bars_found=3 for ticker=MBB",
        observed_matches_expected=True,
    )

    assert record.verification_status == "passed"


def test_evaluate_simple_false_yields_failed() -> None:
    loop = VerificationLoop()
    record = loop.evaluate_simple(
        loop.mark_executed(
            loop.start(
                intended_action="run market_data_worker",
                expected_change="bounded payload should exist",
            ),
            executed_action="market_data_worker.run(ticker=VCB, timeframe=1D)",
        ),
        observed_outcome="worker returned bars_found=0 for ticker=VCB",
        observed_matches_expected=False,
    )

    assert record.verification_status == "failed"


def test_evaluate_simple_none_yields_unknown() -> None:
    loop = VerificationLoop()
    record = loop.evaluate_simple(
        loop.mark_executed(
            loop.start(
                intended_action="inspect an external side effect",
                expected_change="external state changed",
            ),
            executed_action="manual inspection requested",
        ),
        observed_outcome="no authoritative observation was possible",
        observed_matches_expected=None,
    )

    assert record.verification_status == "unknown"


def test_export_stays_compact_and_explicit() -> None:
    loop = VerificationLoop()
    exported = loop.finalize(
        loop.start(
            intended_action="run market_data_worker",
            expected_change="bounded payload should exist",
        ),
        observed_outcome="worker returned bars_found=3 for ticker=MBB",
        verification_status="passed",
    ).to_dict()

    assert set(exported.keys()) == {
        "intended_action",
        "executed_action",
        "expected_change",
        "observed_outcome",
        "verification_status",
    }


def test_no_sleep_logic_is_introduced() -> None:
    loop = VerificationLoop()
    exported = loop.start(
        intended_action="run market_data_worker",
        expected_change="bounded payload should exist",
    ).to_dict()

    assert "sleep_state" not in exported
    assert "wake_state" not in exported


def test_no_broad_runtime_authority_creep_is_introduced() -> None:
    loop = VerificationLoop()
    exported = loop.start(
        intended_action="run market_data_worker",
        expected_change="bounded payload should exist",
    ).to_dict()

    assert "tool_call" not in exported
    assert "orchestration_plan" not in exported
    assert "persistence_write" not in exported
