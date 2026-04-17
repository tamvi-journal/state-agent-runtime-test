from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from state.live_state import LiveState
from state.state_manager import StateManager
from verification.verification_record import VerificationRecord
from .synthesis_gate import SynthesisGate

RenderMode = Literal["builder", "user"]


@dataclass(slots=True)
class MainBrain:
    state_manager: StateManager
    synthesis_gate: SynthesisGate = field(default_factory=SynthesisGate)

    def get_live_state(self) -> LiveState:
        return self.state_manager.get_state()

    def interpret_request(self, user_text: str) -> dict[str, Any]:
        cleaned = user_text.strip()
        lowered = cleaned.lower()

        needs_market_data = any(
            token in lowered for token in ["load", "market data", "daily data", "ohlcv", "ticker"]
        )
        ticker_candidate = self._extract_ticker_candidate(cleaned)

        return {
            "user_text": cleaned,
            "needs_worker": needs_market_data and bool(ticker_candidate),
            "worker_name": "market_data_worker" if needs_market_data and ticker_candidate else None,
            "ticker": ticker_candidate,
            "task_type": "market_data_lookup" if needs_market_data and ticker_candidate else "direct_response",
        }

    def should_call_worker(self, interpreted: dict[str, Any]) -> bool:
        return bool(interpreted.get("needs_worker", False))

    def build_direct_response(
        self,
        user_text: str,
        *,
        render_mode: RenderMode = "user",
        monitor_summary: dict[str, Any] | None = None,
    ) -> str:
        intervention = self._monitor_intervention(monitor_summary)

        if render_mode == "builder":
            base = (
                "Main brain read the request, but no worker path was selected. "
                "Current phase only supports the bounded market-data flow."
            )
            if intervention != "none":
                base += f" Monitor intervention in effect: {intervention}."
            return base

        if intervention == "ask_clarify":
            return (
                "I can continue, but the current turn may still be ambiguous. "
                "I should clarify the target before pretending the route is obvious."
            )

        return (
            "I read the request, but this runtime currently supports only the first bounded "
            "market-data path."
        )

    def synthesize_worker_result(
        self,
        *,
        interpreted: dict[str, Any],
        worker_payload: dict[str, Any],
        verification_record: VerificationRecord | None = None,
        render_mode: RenderMode = "user",
        monitor_summary: dict[str, Any] | None = None,
    ) -> str:
        normalized = self.synthesis_gate.normalize(worker_payload)
        result = normalized["result"]
        warnings = normalized.get("warnings", [])
        confidence = normalized.get("confidence", 0.0)
        worker_name = normalized.get("worker_name", "unknown_worker")
        ticker = interpreted.get("ticker", "")

        intervention = self._monitor_intervention(monitor_summary)

        if render_mode == "builder":
            return self._render_builder_mode(
                worker_name=worker_name,
                ticker=ticker,
                result=result,
                warnings=warnings,
                confidence=confidence,
                verification_record=verification_record,
                monitor_summary=monitor_summary,
            )

        return self._render_user_mode(
            worker_name=worker_name,
            ticker=ticker,
            result=result,
            warnings=warnings,
            verification_record=verification_record,
            intervention=intervention,
            monitor_summary=monitor_summary,
        )

    def handle_request(
        self,
        user_text: str,
        *,
        worker_payload: dict[str, Any] | None = None,
        verification_record: VerificationRecord | None = None,
        render_mode: RenderMode = "user",
        monitor_summary: dict[str, Any] | None = None,
    ) -> str:
        interpreted = self.interpret_request(user_text)

        if not self.should_call_worker(interpreted):
            return self.build_direct_response(
                user_text,
                render_mode=render_mode,
                monitor_summary=monitor_summary,
            )

        if worker_payload is None:
            ticker = interpreted.get("ticker", "")
            if render_mode == "builder":
                msg = (
                    f"Main brain selected market_data_worker for ticker {ticker}, "
                    "but the worker has not been executed yet."
                )
                if monitor_summary:
                    msg += f" monitor_summary={monitor_summary}"
                return msg

            intervention = self._monitor_intervention(monitor_summary)
            if intervention == "ask_clarify":
                return (
                    f"I selected the market-data worker for {ticker}, "
                    "but I should clarify the route before treating it as settled."
                )
            return f"I selected the market-data worker for {ticker}, but it has not run yet."

        return self.synthesize_worker_result(
            interpreted=interpreted,
            worker_payload=worker_payload,
            verification_record=verification_record,
            render_mode=render_mode,
            monitor_summary=monitor_summary,
        )

    def _render_builder_mode(
        self,
        *,
        worker_name: str,
        ticker: str,
        result: dict[str, Any],
        warnings: list[str],
        confidence: float,
        verification_record: VerificationRecord | None,
        monitor_summary: dict[str, Any] | None,
    ) -> str:
        lines: list[str] = []

        lines.append(f"Main brain used {worker_name} for ticker {ticker}.")
        lines.append(f"Worker confidence: {confidence:.2f}")

        latest_bar = result.get("latest_bar")
        if latest_bar:
            lines.append(
                "Latest bar: "
                f"{latest_bar.get('date', '?')} | "
                f"open={latest_bar.get('open', '?')} "
                f"high={latest_bar.get('high', '?')} "
                f"low={latest_bar.get('low', '?')} "
                f"close={latest_bar.get('close', '?')} "
                f"volume={latest_bar.get('volume', '?')}"
            )

        integrity_checks = result.get("integrity_checks")
        if integrity_checks:
            lines.append(f"Integrity checks: {integrity_checks}")

        data_source = result.get("data_source")
        if data_source:
            lines.append(f"Data source: {data_source}")

        bars_found = result.get("bars_found")
        lines.append(f"Bars found: {bars_found}")

        if verification_record is not None:
            lines.append(f"Verification status: {verification_record.verification_status}")
            if verification_record.observed_outcome:
                lines.append(f"Observed outcome: {verification_record.observed_outcome}")

        if monitor_summary:
            lines.append(f"Monitor summary: {monitor_summary}")

        if warnings:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in warnings)

        lines.append("Final note: this is a bounded market-data response, not a trading judgment.")
        return "\n".join(lines)

    def _render_user_mode(
        self,
        *,
        worker_name: str,
        ticker: str,
        result: dict[str, Any],
        warnings: list[str],
        verification_record: VerificationRecord | None,
        intervention: str,
        monitor_summary: dict[str, Any] | None,
    ) -> str:
        lines: list[str] = []

        latest_bar = result.get("latest_bar")
        data_source = result.get("data_source", "")
        integrity_checks = result.get("integrity_checks", {})
        bars_found = result.get("bars_found", 0)

        lines.append(f"I checked {ticker} using {worker_name}.")

        if bars_found == 0:
            lines.append("No bars were returned for this ticker in the current dataset.")
        elif latest_bar:
            lines.append(
                f"Latest daily bar: {latest_bar.get('date', '?')} — "
                f"open {latest_bar.get('open', '?')}, "
                f"high {latest_bar.get('high', '?')}, "
                f"low {latest_bar.get('low', '?')}, "
                f"close {latest_bar.get('close', '?')}, "
                f"volume {latest_bar.get('volume', '?')}."
            )

        if data_source:
            lines.append(f"Source: {data_source}")

        integrity_summary = self._summarize_integrity_checks(integrity_checks)
        if integrity_summary:
            lines.append(integrity_summary)

        if verification_record is not None:
            if verification_record.verification_status == "passed":
                lines.append("Verification passed.")
            elif verification_record.verification_status == "failed":
                lines.append("Verification failed.")
            else:
                lines.append("Verification is unknown.")

        if intervention == "do_not_mark_complete":
            lines.append("Monitor note: do not treat this as complete until observed change is verified.")
        elif intervention == "ask_clarify":
            lines.append("Monitor note: ambiguity may still be active, so this should stay tentative.")
        elif intervention == "restore_mode":
            lines.append("Monitor note: response posture should stay aligned with the active mode.")
        elif intervention == "tighten_project_focus":
            lines.append("Monitor note: keep the answer tied to the active project, not generic filler.")
        elif intervention == "reduce_archive_weight":
            lines.append("Monitor note: keep live state ahead of retrieval weight in this turn.")

        if monitor_summary and monitor_summary.get("primary_risk") not in {None, "", "none"}:
            lines.append(f"Primary governance risk: {monitor_summary['primary_risk']}.")

        if warnings:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in warnings)

        lines.append("This is a bounded market-data read, not a trading judgment.")
        return "\n".join(lines)

    @staticmethod
    def _summarize_integrity_checks(integrity_checks: dict[str, Any]) -> str:
        if not integrity_checks:
            return ""

        parts: list[str] = []
        if integrity_checks.get("file_exists") is False:
            parts.append("data file missing")
        if integrity_checks.get("required_columns_present") is False:
            parts.append("required columns missing")
        if integrity_checks.get("ticker_match_found") is False:
            parts.append("ticker not found in dataset")
        if integrity_checks.get("missing_dates_detected"):
            parts.append("dates appear missing or unsorted")
        if integrity_checks.get("duplicate_dates_detected"):
            parts.append("duplicate dates detected")
        if integrity_checks.get("volume_null_detected"):
            parts.append("some volume values could not be parsed")
        if integrity_checks.get("price_order_valid") is False:
            parts.append("OHLC ordering failed basic validation")

        if not parts:
            return "Integrity summary: basic checks passed."

        return "Integrity summary: " + "; ".join(parts) + "."

    @staticmethod
    def _extract_ticker_candidate(user_text: str) -> str | None:
        for token in user_text.replace(",", " ").split():
            cleaned = token.strip().upper()
            if cleaned.isalpha() and 2 <= len(cleaned) <= 6:
                if cleaned in {"LOAD", "DAILY", "DATA", "TICKER", "MARKET", "OHLCV"}:
                    continue
                return cleaned
        return None

    @staticmethod
    def _monitor_intervention(monitor_summary: dict[str, Any] | None) -> str:
        if not monitor_summary:
            return "none"
        return str(monitor_summary.get("recommended_intervention", "none"))
