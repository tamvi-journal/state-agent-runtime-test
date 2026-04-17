from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from observability.trace_events import TraceEvents
from verification.verification_loop import VerificationLoop
from verification.verification_record import VerificationRecord
from workers.market_data_worker import MarketDataWorker


@dataclass(slots=True)
class ExecutionGate:
    """
    Bounded execution gate for the first worker path.

    Responsibilities:
    - execute one allowed worker
    - create a verification record
    - emit trace/verification events
    - return evidence to main brain

    Non-goals:
    - no multi-worker orchestration
    - no autonomous chains
    """

    market_data_worker: MarketDataWorker
    verification_loop: VerificationLoop
    trace_events: TraceEvents

    def run_market_data_flow(
        self,
        *,
        ticker: str,
        timeframe: str = "1D",
        data_path_expected: str | None = None,
    ) -> tuple[dict[str, Any], VerificationRecord]:
        """
        Execute the first bounded worker path:
        1) create verification record
        2) run worker
        3) observe simple outcome
        4) finalize verification
        5) emit traces
        """
        record = self.verification_loop.start(
            intended_action=f"run market_data_worker for ticker={ticker}",
            expected_change=f"bounded market-data payload should exist for ticker={ticker}",
        )

        record = self.verification_loop.mark_executed(
            record,
            executed_action=f"market_data_worker.run(ticker={ticker}, timeframe={timeframe})",
        )

        payload = self.market_data_worker.run(ticker=ticker, timeframe=timeframe)

        worker_name = payload["worker_name"]
        confidence = payload["confidence"]
        trace = payload["trace"]
        self.trace_events.log_worker_trace(
            worker_name=worker_name,
            trace=trace,
            confidence=confidence,
        )

        # simple phase-1 observation:
        # if bars_found > 0, treat as passed
        # if file missing or ticker missing, treat as failed
        result = payload["result"]
        bars_found = int(result.get("bars_found", 0))

        observed_outcome = (
            f"worker={worker_name} returned bars_found={bars_found} "
            f"for ticker={result.get('ticker', '')}"
        )

        observed_matches_expected: bool | None
        if bars_found > 0:
            observed_matches_expected = True
        else:
            observed_matches_expected = False

        # if caller explicitly says external inspection is impossible, preserve unknown path
        if data_path_expected is None and bars_found == 0:
            # still failed here because we observed a concrete empty result
            observed_matches_expected = False

        record = self.verification_loop.evaluate_simple(
            record,
            observed_outcome=observed_outcome,
            observed_matches_expected=observed_matches_expected,
        )

        self.trace_events.log_verification_event(record=record)
        return payload, record
