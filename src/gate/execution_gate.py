from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from observability.trace_events import TraceEvents
from verification.verification_loop import VerificationLoop
from verification.verification_record import VerificationRecord
from workers.candle_volume_structure_worker import CandleVolumeStructureWorker
from workers.macro_sector_mapping_worker import MacroSectorMappingWorker
from workers.market_data_worker import MarketDataWorker
from workers.sector_flow_worker import SectorFlowWorker
from workers.technical_analysis_worker import TechnicalAnalysisWorker
from workers.trade_memo_worker import TradeMemoWorker


ALLOWED_GATE_DECISIONS = {"allow", "sandbox_only", "needs_approval", "deny"}


@dataclass(slots=True)
class GateDecision:
    decision: str
    action_name: str
    reason: str

    def __post_init__(self) -> None:
        if self.decision not in ALLOWED_GATE_DECISIONS:
            raise ValueError(f"invalid decision: {self.decision}")
        if not isinstance(self.action_name, str) or not self.action_name.strip():
            raise ValueError("action_name must be a non-empty string")
        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ExecutionGate:
    """
    Thin execution gate for the single harness path.

    Responsibilities:
    - decide whether an action is allowed
    - keep all meaningful execution behind one gate
    - execute one allowed local worker path
    - create a verification record
    - emit trace/verification events
    - return evidence to main brain

    Non-goals:
    - no multi-worker orchestration
    - no autonomous chains
    """

    market_data_worker: MarketDataWorker
    technical_analysis_worker: TechnicalAnalysisWorker
    macro_sector_mapping_worker: MacroSectorMappingWorker
    sector_flow_worker: SectorFlowWorker
    candle_volume_structure_worker: CandleVolumeStructureWorker
    trade_memo_worker: TradeMemoWorker
    verification_loop: VerificationLoop
    trace_events: TraceEvents

    def decide(self, *, action_name: str) -> GateDecision:
        normalized = action_name.strip().lower()

        if normalized in {"market_data_lookup", "technical_analysis", "macro_sector_mapping", "sector_flow", "candle_volume_structure", "trade_memo"}:
            return GateDecision(
                decision="sandbox_only",
                action_name=action_name,
                reason="local bounded worker execution is allowed only inside the thin harness surface",
            )
        if normalized in {"write_file", "shell_execute", "network_access", "package_install"}:
            return GateDecision(
                decision="needs_approval",
                action_name=action_name,
                reason="the thin harness does not auto-approve mutable or external actions",
            )
        return GateDecision(
            decision="deny",
            action_name=action_name,
            reason="unsupported action for the thin runtime harness",
        )

    def run_market_data_flow(
        self,
        *,
        ticker: str,
        timeframe: str = "1D",
        data_path_expected: str | None = None,
    ) -> tuple[GateDecision, dict[str, Any] | None, VerificationRecord | None]:
        """
        Execute the first bounded worker path:
        1) gate decision
        2) create verification record
        3) run worker
        4) observe simple outcome
        5) finalize verification
        6) emit traces
        """
        decision = self.decide(action_name="market_data_lookup")
        if decision.decision not in {"allow", "sandbox_only"}:
            return decision, None, None

        record = self.verification_loop.start(
            intended_action=(
                f"permit the market-data path so market_data_worker may call "
                f"market_data_tool.load_market_data for ticker={ticker}"
            ),
            expected_change=f"bounded market-data evidence should exist for ticker={ticker}",
        )

        record = self.verification_loop.mark_executed(
            record,
            executed_action=(
                f"execution path ran market_data_worker.run -> "
                f"market_data_tool.load_market_data("
                f"ticker={ticker}, timeframe={timeframe})"
            ),
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
            f"verification observed worker={worker_name} return tool-derived evidence "
            f"with bars_found={bars_found} for ticker={result.get('ticker', '')}"
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
        return decision, payload, record

    def run_macro_sector_mapping_flow(
        self,
        *,
        macro_signal_payload: dict[str, Any] | None,
    ) -> tuple[GateDecision, dict[str, Any] | None, VerificationRecord | None]:
        decision = self.decide(action_name="macro_sector_mapping")
        if decision.decision not in {"allow", "sandbox_only"}:
            return decision, None, None

        record = self.verification_loop.start(
            intended_action=(
                "permit the macro-sector-mapping path so macro_sector_mapping_worker may "
                "use explicit normalized macro input with the canonical trigger-map config"
            ),
            expected_change="bounded macro-sector bias evidence should exist",
        )

        record = self.verification_loop.mark_executed(
            record,
            executed_action=(
                "execution path ran macro_sector_mapping_worker.run("
                "macro_signal_payload=<explicit structured input>)"
            ),
        )

        payload = self.macro_sector_mapping_worker.run(macro_signal_payload=macro_signal_payload)

        worker_name = payload["worker_name"]
        confidence = payload["confidence"]
        trace = payload["trace"]
        self.trace_events.log_worker_trace(
            worker_name=worker_name,
            trace=trace,
            confidence=confidence,
        )

        result = payload["result"]
        input_status = str(result.get("input_status", "missing"))
        matched_count = len(result.get("matched_signals", []))
        bias_count = len(result.get("vn_sector_bias", []))
        conflict_count = len(result.get("conflict_flags", []))
        observed_outcome = (
            f"verification observed worker={worker_name} produce macro-sector bias evidence "
            f"with input_status={input_status}, matched_signals={matched_count}, "
            f"vn_sector_bias={bias_count}, conflict_flags={conflict_count}"
        )
        observed_matches_expected = input_status in {"loaded", "partial"} and matched_count > 0 and bias_count > 0

        record = self.verification_loop.evaluate_simple(
            record,
            observed_outcome=observed_outcome,
            observed_matches_expected=observed_matches_expected,
        )

        self.trace_events.log_verification_event(record=record)
        return decision, payload, record

    def run_sector_flow(
        self,
        *,
        sector_flow_payload: dict[str, Any] | None,
        macro_sector_bias_payload: dict[str, Any] | None = None,
    ) -> tuple[GateDecision, dict[str, Any] | None, VerificationRecord | None]:
        decision = self.decide(action_name="sector_flow")
        if decision.decision not in {"allow", "sandbox_only"}:
            return decision, None, None

        record = self.verification_loop.start(
            intended_action=(
                "permit the sector-flow path so sector_flow_worker may classify explicit sector metrics "
                "using canonical state-rule and sector-universe config"
            ),
            expected_change="bounded sector-state evidence should exist",
        )

        record = self.verification_loop.mark_executed(
            record,
            executed_action=(
                "execution path ran sector_flow_worker.run("
                "sector_flow_payload=<explicit structured input>, "
                "macro_sector_bias_payload=<optional explicit input>)"
            ),
        )

        payload = self.sector_flow_worker.run(
            sector_flow_payload=sector_flow_payload,
            macro_sector_bias_payload=macro_sector_bias_payload,
        )

        worker_name = payload["worker_name"]
        confidence = payload["confidence"]
        trace = payload["trace"]
        self.trace_events.log_worker_trace(
            worker_name=worker_name,
            trace=trace,
            confidence=confidence,
        )

        result = payload["result"]
        input_status = str(result.get("input_status", "missing"))
        board_count = len(result.get("sector_flow_board", []))
        unclassified_count = len(result.get("unclassified_sectors", []))
        conflict_count = len(result.get("conflict_flags", []))
        observed_outcome = (
            f"verification observed worker={worker_name} produce sector-state evidence "
            f"from explicit metrics with input_status={input_status}, "
            f"sector_flow_board={board_count}, unclassified_sectors={unclassified_count}, "
            f"conflict_flags={conflict_count}"
        )
        observed_matches_expected = input_status in {"loaded", "partial"} and board_count > 0

        record = self.verification_loop.evaluate_simple(
            record,
            observed_outcome=observed_outcome,
            observed_matches_expected=observed_matches_expected,
        )

        self.trace_events.log_verification_event(record=record)
        return decision, payload, record

    def run_candle_volume_structure(
        self,
        *,
        candidate_payload: dict[str, Any] | None,
    ) -> tuple[GateDecision, dict[str, Any] | None, VerificationRecord | None]:
        decision = self.decide(action_name="candle_volume_structure")
        if decision.decision not in {"allow", "sandbox_only"}:
            return decision, None, None

        record = self.verification_loop.start(
            intended_action=(
                "permit the candle-volume-structure path so candle_volume_structure_worker may score "
                "explicit stock candidates using canonical hard-filter rules"
            ),
            expected_change="bounded top-watch setup evidence should exist",
        )

        record = self.verification_loop.mark_executed(
            record,
            executed_action=(
                "execution path ran candle_volume_structure_worker.run("
                "candidate_payload=<explicit structured input>)"
            ),
        )

        payload = self.candle_volume_structure_worker.run(candidate_payload=candidate_payload)

        worker_name = payload["worker_name"]
        confidence = payload["confidence"]
        trace = payload["trace"]
        self.trace_events.log_worker_trace(
            worker_name=worker_name,
            trace=trace,
            confidence=confidence,
        )

        result = payload["result"]
        input_status = str(result.get("input_status", "missing"))
        top_count = len(result.get("top_list", []))
        watch_count = len(result.get("watch_list", []))
        rejected_count = len(result.get("rejected", []))
        observed_outcome = (
            f"verification observed worker={worker_name} produce setup evidence "
            f"from explicit candidates with input_status={input_status}, "
            f"top_list={top_count}, watch_list={watch_count}, rejected={rejected_count}"
        )
        observed_matches_expected = input_status in {"loaded", "partial"} and (top_count > 0 or watch_count > 0)

        record = self.verification_loop.evaluate_simple(
            record,
            observed_outcome=observed_outcome,
            observed_matches_expected=observed_matches_expected,
        )

        self.trace_events.log_verification_event(record=record)
        return decision, payload, record

    def run_trade_memo(
        self,
        *,
        memo_payload: dict[str, Any] | None,
    ) -> tuple[GateDecision, dict[str, Any] | None, VerificationRecord | None]:
        decision = self.decide(action_name="trade_memo")
        if decision.decision not in {"allow", "sandbox_only"}:
            return decision, None, None

        record = self.verification_loop.start(
            intended_action=(
                "permit the trade-memo path so trade_memo_worker may build bounded scenario memo evidence "
                "from explicit shortlisted ticker input"
            ),
            expected_change="bounded trade memo evidence should exist",
        )

        record = self.verification_loop.mark_executed(
            record,
            executed_action=(
                "execution path ran trade_memo_worker.run("
                "memo_payload=<explicit structured input>)"
            ),
        )

        payload = self.trade_memo_worker.run(memo_payload=memo_payload)

        worker_name = payload["worker_name"]
        confidence = payload["confidence"]
        trace = payload["trace"]
        self.trace_events.log_worker_trace(
            worker_name=worker_name,
            trace=trace,
            confidence=confidence,
        )

        result = payload["result"]
        input_status = str(result.get("input_status", "missing"))
        memo_mode_effective = str(result.get("memo_mode_effective", "lite"))
        memo_count = len(result.get("ticker_memos", []))
        observed_outcome = (
            f"verification observed worker={worker_name} produce structured memo evidence "
            f"from explicit ticker input with input_status={input_status}, "
            f"memo_mode_effective={memo_mode_effective}, ticker_memos={memo_count}"
        )
        observed_matches_expected = input_status in {"loaded", "partial"} and memo_count > 0

        record = self.verification_loop.evaluate_simple(
            record,
            observed_outcome=observed_outcome,
            observed_matches_expected=observed_matches_expected,
        )

        self.trace_events.log_verification_event(record=record)
        return decision, payload, record

    def run_technical_analysis_flow(
        self,
        *,
        ticker: str,
        timeframe: str = "1D",
    ) -> tuple[GateDecision, dict[str, Any] | None, VerificationRecord | None]:
        decision = self.decide(action_name="technical_analysis")
        if decision.decision not in {"allow", "sandbox_only"}:
            return decision, None, None

        record = self.verification_loop.start(
            intended_action=(
                f"permit the technical-analysis path so technical_analysis_worker may call "
                f"market_data_tool.load_market_data for ticker={ticker}"
            ),
            expected_change=f"bounded technical-analysis evidence should exist for ticker={ticker}",
        )

        record = self.verification_loop.mark_executed(
            record,
            executed_action=(
                f"execution path ran technical_analysis_worker.run -> "
                f"market_data_tool.load_market_data("
                f"ticker={ticker}, timeframe={timeframe})"
            ),
        )

        payload = self.technical_analysis_worker.run(ticker=ticker, timeframe=timeframe)

        worker_name = payload["worker_name"]
        confidence = payload["confidence"]
        trace = payload["trace"]
        self.trace_events.log_worker_trace(
            worker_name=worker_name,
            trace=trace,
            confidence=confidence,
        )

        result = payload["result"]
        data_status = str(result.get("data_status", "missing"))
        bars_found = int(result.get("bars_found", 0))
        alignment_status = str(result.get("alignment_status", "unresolved"))
        observed_outcome = (
            f"verification observed worker={worker_name} produce technical-analysis evidence "
            f"from local bounded market data with data_status={data_status}, "
            f"bars_found={bars_found}, alignment_status={alignment_status} "
            f"for ticker={result.get('symbol', '')}"
        )
        observed_matches_expected = data_status in {"loaded", "partial"} and bars_found > 0

        record = self.verification_loop.evaluate_simple(
            record,
            observed_outcome=observed_outcome,
            observed_matches_expected=observed_matches_expected,
        )

        self.trace_events.log_verification_event(record=record)
        return decision, payload, record
