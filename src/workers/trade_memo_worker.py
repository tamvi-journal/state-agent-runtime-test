from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from workers.contracts import WorkerContractValidator


@dataclass(slots=True)
class TradeMemoWorker:
    """
    Bounded Engine C trade memo worker for the thin runtime harness.

    Responsibilities:
    - receive explicit shortlisted ticker input
    - summarize setup quality honestly
    - build rounded, conditional scenario branches
    - return structured memo evidence for the brain

    Non-goals:
    - no final report prose as primary output
    - no auto-execution behavior
    - no pseudo-full portfolio planning
    """

    validator: WorkerContractValidator | None = None

    def __post_init__(self) -> None:
        if self.validator is None:
            self.validator = WorkerContractValidator()

    def run(
        self,
        *,
        memo_payload: dict[str, Any] | None,
    ) -> dict[str, Any]:
        trace = [
            "received explicit trade-memo request",
            "using Engine C method: setup summary -> three conditional scenarios -> action today -> risk/invalidation",
        ]
        assumptions = [
            "trade memo input is supplied explicitly to this worker",
            "scenario probabilities are rounded conditional estimates rather than predictions",
            "full mode is not implemented in this bounded worker and is downshifted honestly to lite",
        ]
        warnings: list[str] = []

        extracted = self._extract_inputs(memo_payload=memo_payload)
        trace.extend(extracted["trace"])
        warnings.extend(extracted["warnings"])

        memo_mode_requested = extracted["memo_mode_requested"]
        memo_mode_effective = "lite"
        if memo_mode_requested == "full":
            warnings.append("full-mode extras are not implemented in this bounded worker yet; memo_mode_effective=lite")

        ticker_memos: list[dict[str, Any]] = []
        if extracted["ticker_inputs"]:
            for ticker_input in extracted["ticker_inputs"]:
                memo = self._build_ticker_memo(ticker_input=ticker_input)
                if memo is not None:
                    ticker_memos.append(memo)
        else:
            warnings.append("trade memo could not proceed because explicit ticker input was missing")

        confidence = self._confidence(
            input_status=extracted["input_status"],
            memo_count=len(ticker_memos),
            warning_count=len(warnings),
        )

        payload = {
            "worker_name": "trade_memo_worker",
            "result": {
                "task_type": "trade_memo",
                "input_status": extracted["input_status"],
                "memo_mode_requested": memo_mode_requested,
                "memo_mode_effective": memo_mode_effective,
                "ticker_memos": ticker_memos,
            },
            "confidence": confidence,
            "assumptions": assumptions,
            "warnings": warnings,
            "trace": trace + ["trade memo worker packaged structured scenario-based memo evidence for the brain"],
            "proposed_memory_update": None,
        }
        return self.validator.validate(payload)

    @staticmethod
    def _extract_inputs(*, memo_payload: dict[str, Any] | None) -> dict[str, Any]:
        trace: list[str] = []
        warnings: list[str] = []
        if not isinstance(memo_payload, dict):
            return {
                "input_status": "missing",
                "memo_mode_requested": "lite",
                "ticker_inputs": [],
                "trace": trace + ["no explicit trade memo payload was supplied to the worker"],
                "warnings": warnings,
            }

        payload_data = memo_payload.get("data", memo_payload)
        if not isinstance(payload_data, dict):
            return {
                "input_status": "missing",
                "memo_mode_requested": "lite",
                "ticker_inputs": [],
                "trace": trace + ["trade memo payload was present but did not contain a structured data object"],
                "warnings": warnings,
            }

        memo_mode_requested = str(payload_data.get("memo_mode", "lite") or "lite").strip().lower()
        raw_ticker_inputs = payload_data.get("ticker_inputs", [])
        if not isinstance(raw_ticker_inputs, list):
            return {
                "input_status": "missing",
                "memo_mode_requested": memo_mode_requested,
                "ticker_inputs": [],
                "trace": trace + ["trade memo payload did not contain a valid ticker_inputs list"],
                "warnings": warnings,
            }

        valid_inputs: list[dict[str, Any]] = []
        partial = False
        for item in raw_ticker_inputs[:5]:
            if not isinstance(item, dict):
                partial = True
                continue
            if not item.get("ticker") or not item.get("current_price"):
                partial = True
                continue
            valid_inputs.append(item)

        if not valid_inputs:
            input_status = "missing"
        elif partial:
            input_status = "partial"
        else:
            input_status = "loaded"

        if partial:
            warnings.append("one or more ticker memo inputs were incomplete and were skipped")

        return {
            "input_status": input_status,
            "memo_mode_requested": memo_mode_requested,
            "ticker_inputs": valid_inputs,
            "trace": trace + [f"received {len(valid_inputs)} usable trade memo inputs"],
            "warnings": warnings,
        }

    def _build_ticker_memo(self, *, ticker_input: dict[str, Any]) -> dict[str, Any] | None:
        setup_summary = self._setup_summary(ticker_input=ticker_input)
        scenario_table = self._scenario_table(ticker_input=ticker_input, setup_summary=setup_summary)
        if not scenario_table:
            return None

        action_today = self._action_today(ticker_input=ticker_input, setup_summary=setup_summary)
        risk_plan = self._risk_plan(ticker_input=ticker_input, setup_summary=setup_summary)

        return {
            "ticker": str(ticker_input.get("ticker", "")),
            "sector": str(ticker_input.get("sector", "")),
            "setup_summary": setup_summary,
            "scenario_table": scenario_table,
            "action_today": action_today,
            "risk_plan": risk_plan,
        }

    @staticmethod
    def _setup_summary(*, ticker_input: dict[str, Any]) -> dict[str, Any]:
        sector_state = str(ticker_input.get("sector_state", ""))
        why_in = [str(item) for item in ticker_input.get("why_in", []) if str(item)]
        why_not_top = [str(item) for item in ticker_input.get("why_not_top", []) if str(item)]
        risk_note = [str(item) for item in ticker_input.get("risk_note", []) if str(item)]
        trend_quality = float(ticker_input.get("trend_quality_score", 0.0) or 0.0)
        volume_confirmation = float(ticker_input.get("volume_confirmation_score", 0.0) or 0.0)
        setup_readiness = float(ticker_input.get("setup_readiness_score", 0.0) or 0.0)

        if trend_quality >= 7.8 and volume_confirmation >= 7.0 and setup_readiness >= 7.8 and not why_not_top:
            status = "active_setup"
        elif trend_quality >= 6.0 and setup_readiness >= 6.0:
            status = "watch_setup"
        else:
            status = "thin_setup"

        good_points = list(why_in)
        if sector_state:
            good_points.append(f"sector_{sector_state.lower()}")
        if float(ticker_input.get("current_price", 0.0) or 0.0) > float(ticker_input.get("ma20", 0.0) or 0.0) > 0:
            good_points.append("above_ma20")

        missing_points = list(why_not_top)
        if not why_not_top and status != "active_setup":
            missing_points.append("setup_confirmation_still_limited")
        if not risk_note and status != "active_setup":
            missing_points.append("risk_context_thin")

        main_risk = risk_note[0] if risk_note else "setup needs more confirmation before confidence can improve"
        return {
            "status": status,
            "good_points": good_points[:4],
            "missing_points": missing_points[:4],
            "main_risk": main_risk,
        }

    def _scenario_table(
        self,
        *,
        ticker_input: dict[str, Any],
        setup_summary: dict[str, Any],
    ) -> list[dict[str, Any]]:
        current_price = float(ticker_input.get("current_price", 0.0) or 0.0)
        if current_price <= 0:
            return []

        status = str(setup_summary.get("status", "thin_setup"))
        support_zone = str(ticker_input.get("support_zone", ""))
        resistance_zone = str(ticker_input.get("resistance_zone", ""))
        sector_state = str(ticker_input.get("sector_state", ""))
        catalyst_note = str(ticker_input.get("catalyst_note", "")).strip()

        if status == "active_setup":
            probabilities = {"bullish": 50, "neutral": 30, "bearish": 20}
            bullish_timeline = "2-6 weeks"
            neutral_timeline = "2-4 weeks"
            bearish_timeline = "1-3 weeks"
            bullish_target = self._zone_from_price(current_price=current_price, low_mult=1.08, high_mult=1.14)
        elif status == "watch_setup":
            probabilities = {"bullish": 40, "neutral": 35, "bearish": 25}
            bullish_timeline = "3-8 weeks"
            neutral_timeline = "2-5 weeks"
            bearish_timeline = "1-4 weeks"
            bullish_target = self._zone_from_price(current_price=current_price, low_mult=1.05, high_mult=1.1)
        else:
            probabilities = {"bullish": 30, "neutral": 35, "bearish": 35}
            bullish_timeline = "3-8 weeks"
            neutral_timeline = "2-5 weeks"
            bearish_timeline = "1-4 weeks"
            bullish_target = self._zone_from_price(current_price=current_price, low_mult=1.03, high_mult=1.07)

        neutral_target = resistance_zone or self._zone_from_price(current_price=current_price, low_mult=0.99, high_mult=1.04)
        bearish_target = support_zone or self._zone_from_price(current_price=current_price, low_mult=0.92, high_mult=0.97)

        bullish_triggers = [
            "hold above support zone" if support_zone else "hold above recent support",
            "volume stays at or above average",
            f"sector remains {sector_state} or improves" if sector_state else "sector stays supportive",
        ]
        if catalyst_note:
            bullish_triggers.append("setup remains aligned with the stated catalyst note")

        neutral_triggers = [
            "price stays in a sideways range",
            "volume cools down",
            "market lacks fresh follow-through",
        ]
        bearish_triggers = [
            "lose support zone" if support_zone else "lose recent support",
            "sector weakens",
            "setup follow-through fails",
        ]

        return [
            {
                "scenario": "bullish",
                "probability_pct": probabilities["bullish"],
                "target_zone": bullish_target,
                "timeline": bullish_timeline,
                "triggers": bullish_triggers[:4],
            },
            {
                "scenario": "neutral",
                "probability_pct": probabilities["neutral"],
                "target_zone": neutral_target,
                "timeline": neutral_timeline,
                "triggers": neutral_triggers,
            },
            {
                "scenario": "bearish",
                "probability_pct": probabilities["bearish"],
                "target_zone": bearish_target,
                "timeline": bearish_timeline,
                "triggers": bearish_triggers,
            },
        ]

    @staticmethod
    def _action_today(*, ticker_input: dict[str, Any], setup_summary: dict[str, Any]) -> dict[str, str]:
        status = str(setup_summary.get("status", "thin_setup"))
        why_not_top = [str(item) for item in ticker_input.get("why_not_top", []) if str(item)]
        current_price = float(ticker_input.get("current_price", 0.0) or 0.0)
        resistance_zone = str(ticker_input.get("resistance_zone", ""))

        if status == "active_setup" and not why_not_top:
            stance = "partial_entry"
            reason = "setup quality is stronger, but action remains conditional on follow-through"
            next_best_signal = "hold breakout with volume"
        elif status == "watch_setup":
            if resistance_zone:
                stance = "watch_or_partial_entry"
                reason = "setup is constructive but still has missing confirmation"
                next_best_signal = "clean break over resistance with volume"
            else:
                stance = "watch_only"
                reason = "setup is promising but still incomplete"
                next_best_signal = "stronger price and volume confirmation"
        else:
            stance = "avoid_for_now"
            reason = "ticker evidence is too thin for an honest memo stance"
            next_best_signal = "clear structure plus better confirmation"

        if current_price <= 0:
            stance = "watch_only"
            reason = "price context is incomplete, so action must stay bounded"
            next_best_signal = "complete price context"

        return {
            "stance": stance,
            "reason": reason,
            "next_best_signal": next_best_signal,
        }

    @staticmethod
    def _risk_plan(*, ticker_input: dict[str, Any], setup_summary: dict[str, Any]) -> dict[str, Any]:
        support_zone = str(ticker_input.get("support_zone", "")).strip()
        risk_note = [str(item) for item in ticker_input.get("risk_note", []) if str(item)]
        if not risk_note:
            risk_note = [str(setup_summary.get("main_risk", "risk context remains incomplete"))]

        if support_zone:
            invalidation_zone = f"below {support_zone.split('-')[0].strip()}"
        else:
            ma50 = float(ticker_input.get("ma50", 0.0) or 0.0)
            invalidation_zone = f"below {round(ma50, 1)}" if ma50 > 0 else "support not clearly defined"

        return {
            "invalidation_zone": invalidation_zone,
            "risk_note": risk_note[:3],
        }

    @staticmethod
    def _zone_from_price(*, current_price: float, low_mult: float, high_mult: float) -> str:
        low = round(current_price * low_mult, 1)
        high = round(current_price * high_mult, 1)
        return f"{low}-{high}"

    @staticmethod
    def _confidence(
        *,
        input_status: str,
        memo_count: int,
        warning_count: int,
    ) -> float:
        if input_status == "missing" or memo_count == 0:
            return 0.0

        confidence = 0.76 if input_status == "loaded" else 0.58
        confidence -= min(warning_count, 3) * 0.06
        return max(0.18, min(confidence, 0.84))
