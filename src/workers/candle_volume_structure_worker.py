from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json

from workers.contracts import WorkerContractValidator


@dataclass(slots=True)
class CandleVolumeStructureWorker:
    """
    Bounded candle/volume/structure worker for the thin runtime harness.

    Responsibilities:
    - receive explicit candidate-stock input
    - apply canonical hard filters first
    - score candle, volume, and setup quality conservatively
    - separate Top, Watch, and Reject evidence honestly

    Non-goals:
    - no hidden sample fallback
    - no remote OHLCV fetching
    - no final user-facing market report generation
    """

    hard_filter_rules_path: str | Path = "config/hard_filter_rules_v1.json"
    validator: WorkerContractValidator | None = None
    _hard_filter_rules_cache: dict[str, Any] | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.hard_filter_rules_path = str(self.hard_filter_rules_path)
        if self.validator is None:
            self.validator = WorkerContractValidator()

    def run(
        self,
        *,
        candidate_payload: dict[str, Any] | None,
    ) -> dict[str, Any]:
        trace = [
            "received explicit candle-volume-structure request",
            "using candle-volume-structure method: hard filters -> candle -> volume -> structure/location -> relative context -> explainability -> setup class",
            f"loading canonical hard-filter rules from {self.hard_filter_rules_path}",
        ]
        assumptions = [
            "candidate-stock input is supplied explicitly to this worker",
            "final_score is a lightweight summary only and must not override a weak critical dimension",
            "Top, Watch, and Reject are semantic setup classes rather than numeric score bands",
        ]
        warnings: list[str] = []

        hard_filter_rules, config_error = self._load_hard_filter_rules()
        if config_error is not None:
            warnings.append(config_error)

        candidate_data = self._extract_candidates(candidate_payload=candidate_payload)
        input_status = candidate_data["input_status"]
        stock_candidates = candidate_data["stock_candidates"]
        trace.extend(candidate_data["trace"])
        warnings.extend(candidate_data["warnings"])

        top_list: list[dict[str, Any]] = []
        watch_list: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []

        if hard_filter_rules is not None and stock_candidates:
            for candidate in stock_candidates:
                hard_filter_result = self._apply_hard_filters(
                    candidate=candidate,
                    hard_filter_rules=hard_filter_rules,
                )
                if not hard_filter_result["passed"]:
                    rejected.append(
                        {
                            "ticker": str(candidate.get("ticker", "")),
                            "reason": "hard_filter_failed_or_setup_not_ready",
                            "detail": hard_filter_result["reasons"],
                        }
                    )
                    continue

                evaluation = self._evaluate_candidate(candidate=candidate)
                if evaluation["classification"] == "TOP":
                    top_list.append(evaluation["entry"])
                elif evaluation["classification"] == "WATCH":
                    watch_list.append(evaluation["entry"])
                else:
                    rejected.append(
                        {
                            "ticker": str(candidate.get("ticker", "")),
                            "reason": "hard_filter_failed_or_setup_not_ready",
                            "detail": evaluation["why_not_top"] or evaluation["risk_note"] or ["insufficient_setup_confirmation"],
                        }
                    )
        elif hard_filter_rules is None:
            warnings.append("candle-volume-structure scoring could not proceed because canonical hard-filter config was unavailable")
        elif not stock_candidates:
            warnings.append("candle-volume-structure scoring could not proceed because explicit stock candidates were missing")

        confidence = self._confidence(
            input_status=input_status,
            config_loaded=hard_filter_rules is not None,
            top_count=len(top_list),
            watch_count=len(watch_list),
            rejected_count=len(rejected),
            warning_count=len(warnings),
        )

        payload = {
            "worker_name": "candle_volume_structure_worker",
            "result": {
                "task_type": "candle_volume_structure",
                "input_status": input_status if hard_filter_rules is not None else "missing",
                "top_list": top_list,
                "watch_list": watch_list,
                "rejected": rejected,
                "config_source": self.hard_filter_rules_path,
            },
            "confidence": confidence,
            "assumptions": assumptions,
            "warnings": warnings,
            "trace": trace + ["candle volume structure worker packaged structured setup evidence for the brain"],
            "proposed_memory_update": None,
        }
        return self.validator.validate(payload)

    def _load_hard_filter_rules(self) -> tuple[dict[str, Any] | None, str | None]:
        if self._hard_filter_rules_cache is not None:
            return self._hard_filter_rules_cache, None

        path = Path(self.hard_filter_rules_path)
        if not path.exists():
            return None, "canonical hard filter rules do not exist"

        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None, "canonical hard filter rules could not be parsed"

        if not isinstance(loaded, dict) or not loaded:
            return None, "canonical hard filter rules were empty or invalid"

        self._hard_filter_rules_cache = loaded
        return loaded, None

    @staticmethod
    def _extract_candidates(*, candidate_payload: dict[str, Any] | None) -> dict[str, Any]:
        trace: list[str] = []
        warnings: list[str] = []
        if not isinstance(candidate_payload, dict):
            return {
                "input_status": "missing",
                "stock_candidates": [],
                "trace": trace + ["no explicit candidate payload was supplied to the worker"],
                "warnings": warnings,
            }

        payload_data = candidate_payload.get("data", candidate_payload)
        if not isinstance(payload_data, dict):
            return {
                "input_status": "missing",
                "stock_candidates": [],
                "trace": trace + ["candidate payload was present but did not contain a structured data object"],
                "warnings": warnings,
            }

        raw_candidates = payload_data.get("stock_candidates", [])
        if not isinstance(raw_candidates, list):
            return {
                "input_status": "missing",
                "stock_candidates": [],
                "trace": trace + ["candidate payload did not contain a valid stock_candidates list"],
                "warnings": warnings,
            }

        valid_candidates: list[dict[str, Any]] = []
        partial = False
        for candidate in raw_candidates:
            if not isinstance(candidate, dict):
                partial = True
                continue
            if not candidate.get("ticker") or not candidate.get("sector") or not candidate.get("sector_state"):
                partial = True
                continue
            valid_candidates.append(candidate)

        if not valid_candidates:
            input_status = "missing"
        elif partial:
            input_status = "partial"
        else:
            input_status = "loaded"

        if partial:
            warnings.append("one or more stock candidates were incomplete and were skipped")

        return {
            "input_status": input_status,
            "stock_candidates": valid_candidates,
            "trace": trace + [f"received {len(valid_candidates)} usable stock candidates"],
            "warnings": warnings,
        }

    @staticmethod
    def _apply_hard_filters(
        *,
        candidate: dict[str, Any],
        hard_filter_rules: dict[str, Any],
    ) -> dict[str, Any]:
        rules = hard_filter_rules.get("rules", {})
        reasons: list[str] = []

        liquidity_rule = rules.get("minimum_liquidity", {})
        if liquidity_rule.get("enabled"):
            actual_liquidity = float(candidate.get(liquidity_rule.get("metric", "avg_trading_value_20d_bil_vnd"), 0.0) or 0.0)
            if actual_liquidity < float(liquidity_rule.get("threshold", 0.0)):
                reasons.append("minimum_liquidity_failed")

        rs_rule = rules.get("minimum_rs_score", {})
        if rs_rule.get("enabled"):
            actual_rs = float(candidate.get(rs_rule.get("metric", "rs_score"), 0.0) or 0.0)
            if actual_rs < float(rs_rule.get("threshold", 0.0)):
                reasons.append("minimum_rs_score_failed")

        warning_rule = rules.get("exclude_warning_status", {})
        if warning_rule.get("enabled"):
            warning_status = str(candidate.get(warning_rule.get("field", "warning_status"), "normal")).strip().lower()
            excluded = {str(item).strip().lower() for item in warning_rule.get("exclude_if_in", [])}
            if warning_status in excluded:
                reasons.append("warning_status_excluded")

        illiquid_rule = rules.get("exclude_extreme_illiquid", {})
        if illiquid_rule.get("enabled"):
            actual_volume = float(candidate.get(illiquid_rule.get("metric", "avg_volume_20d"), 0.0) or 0.0)
            if actual_volume < float(illiquid_rule.get("threshold", 0.0)):
                reasons.append("extreme_illiquid")

        breakdown_rule = rules.get("exclude_recent_major_breakdown", {})
        if breakdown_rule.get("enabled"):
            conditions = breakdown_rule.get("conditions", {})
            close_below_ma50_pct = float(candidate.get("close_below_ma50_pct", 0.0) or 0.0)
            breakdown_confirmed = bool(candidate.get("breakdown_confirmed", False))
            if breakdown_confirmed and close_below_ma50_pct <= float(conditions.get("close_below_ma50_pct", 0.0)):
                reasons.append("recent_major_breakdown")

        near_breakdown_rule = rules.get("exclude_near_breakdown_zone", {})
        if near_breakdown_rule.get("enabled"):
            conditions = near_breakdown_rule.get("conditions", {})
            distance_to_support = float(candidate.get("distance_to_recent_support_pct", 999.0) or 999.0)
            support_status = str(candidate.get("support_status", "safe"))
            if (
                distance_to_support <= float(conditions.get("distance_to_recent_support_pct", 0.0))
                and support_status == str(conditions.get("support_status", "at_risk"))
            ):
                reasons.append("near_breakdown_zone")

        sector_rule = rules.get("sector_state_allowed", {})
        if sector_rule.get("enabled"):
            allowed_states = {str(item) for item in sector_rule.get("allowed_states", [])}
            if str(candidate.get("sector_state", "")) not in allowed_states:
                reasons.append("sector_state_not_allowed")

        manual_rule = rules.get("manual_exclusion_list", {})
        if manual_rule.get("enabled"):
            excluded_tickers = {str(item).upper() for item in manual_rule.get("tickers", [])}
            if str(candidate.get("ticker", "")).upper() in excluded_tickers:
                reasons.append("manual_exclusion")

        if candidate.get("price_structure_ok") is False:
            reasons.append("price_structure_not_ok")

        return {
            "passed": not reasons,
            "reasons": reasons,
        }

    def _evaluate_candidate(self, *, candidate: dict[str, Any]) -> dict[str, Any]:
        ohlcv_context = candidate.get("ohlcv_context", {})
        if not isinstance(ohlcv_context, dict):
            ohlcv_context = {}

        candle = self._read_candle(candidate=candidate, ohlcv_context=ohlcv_context)
        volume = self._read_volume(candidate=candidate, ohlcv_context=ohlcv_context)
        structure = self._read_structure(candidate=candidate, ohlcv_context=ohlcv_context)
        relative = self._read_relative_context(candidate=candidate, ohlcv_context=ohlcv_context)

        trend_quality_score = self._trend_quality_score(
            candle=candle,
            structure=structure,
            relative=relative,
        )
        volume_confirmation_score = self._volume_confirmation_score(volume=volume)
        setup_readiness_score = self._setup_readiness_score(
            candle=candle,
            volume=volume,
            structure=structure,
            relative=relative,
        )

        why_in = self._why_in(
            candidate=candidate,
            candle=candle,
            volume=volume,
            structure=structure,
            relative=relative,
        )
        why_not_top = self._why_not_top(
            candle=candle,
            volume=volume,
            structure=structure,
            relative=relative,
        )
        risk_note = self._risk_note(
            candle=candle,
            volume=volume,
            structure=structure,
        )

        classification = self._classify_setup(
            trend_quality_score=trend_quality_score,
            volume_confirmation_score=volume_confirmation_score,
            setup_readiness_score=setup_readiness_score,
            why_not_top=why_not_top,
            risk_note=risk_note,
            ohlcv_context=ohlcv_context,
        )

        final_score = self._final_score(
            classification=classification,
            trend_quality_score=trend_quality_score,
            volume_confirmation_score=volume_confirmation_score,
            setup_readiness_score=setup_readiness_score,
            why_not_top=why_not_top,
        )

        entry = {
            "ticker": str(candidate.get("ticker", "")),
            "sector": str(candidate.get("sector", "")),
            "setup_type": structure["setup_type"],
            "location_type": structure["location_type"],
            "candle_signal": candle["signal"],
            "volume_signal": volume["signal"],
            "close_quality": candle["close_quality"],
            "base_quality": structure["base_quality"],
            "retest_quality": structure["retest_quality"],
            "scores": {
                "trend_quality_score": trend_quality_score,
                "volume_confirmation_score": volume_confirmation_score,
                "setup_readiness_score": setup_readiness_score,
            },
            "why_in": why_in,
            "why_not_top": why_not_top,
            "risk_note": risk_note,
        }
        if final_score is not None:
            entry["scores"]["final_score"] = final_score

        return {
            "classification": classification,
            "entry": entry,
            "why_not_top": why_not_top,
            "risk_note": risk_note,
        }

    @staticmethod
    def _read_candle(*, candidate: dict[str, Any], ohlcv_context: dict[str, Any]) -> dict[str, str]:
        signal = str(ohlcv_context.get("candle_signal", "")).strip()
        if not signal:
            if "rs_strong" in candidate.get("candidate_reason", []):
                signal = "constructive"
            elif "base_forming" in candidate.get("candidate_reason", []):
                signal = "quiet_candle"
            else:
                signal = "unclear"

        close_quality = str(ohlcv_context.get("close_quality", "")).strip()
        if not close_quality:
            if signal in {"bullish_momentum", "constructive"}:
                close_quality = "acceptable"
            elif signal == "quiet_candle":
                close_quality = "neutral"
            else:
                close_quality = "unclear"

        return {
            "signal": signal,
            "close_quality": close_quality,
        }

    @staticmethod
    def _read_volume(*, candidate: dict[str, Any], ohlcv_context: dict[str, Any]) -> dict[str, str | float]:
        volume_signal = str(ohlcv_context.get("volume_signal", "")).strip()
        volume_vs_ma20 = float(ohlcv_context.get("volume_vs_ma20", 0.0) or 0.0)
        if not volume_signal:
            if volume_vs_ma20 >= 1.25:
                volume_signal = "expanded_confirmed"
            elif volume_vs_ma20 >= 0.95:
                volume_signal = "moderate"
            elif volume_vs_ma20 > 0:
                volume_signal = "drying_up"
            else:
                volume_signal = "unclear"

        return {
            "signal": volume_signal,
            "volume_vs_ma20": volume_vs_ma20,
        }

    @staticmethod
    def _read_structure(*, candidate: dict[str, Any], ohlcv_context: dict[str, Any]) -> dict[str, str]:
        setup_type = str(ohlcv_context.get("setup_type", "")).strip()
        note = str(ohlcv_context.get("recent_structure_note", "")).strip().lower()
        if not setup_type:
            if "breakout" in note:
                setup_type = "base_breakout"
            elif "base" in note:
                setup_type = "base_forming"
            elif candidate.get("price_structure_ok"):
                setup_type = "structure_intact"
            else:
                setup_type = "unclear"

        location_type = str(ohlcv_context.get("location_type", "")).strip()
        if not location_type:
            if "resistance" in note:
                location_type = "near_resistance"
            elif "base" in note:
                location_type = "inside_base"
            elif candidate.get("price_structure_ok"):
                location_type = "above_support"
            else:
                location_type = "unclear"

        base_quality = str(ohlcv_context.get("base_quality", "")).strip()
        if not base_quality:
            if "tight" in note:
                base_quality = "tight_base"
            elif candidate.get("price_structure_ok"):
                base_quality = "acceptable"
            else:
                base_quality = "loose"

        retest_quality = str(ohlcv_context.get("retest_quality", "")).strip()
        if not retest_quality:
            if "retest" in note:
                retest_quality = "pending"
            elif setup_type == "base_breakout":
                retest_quality = "not_required"
            else:
                retest_quality = "pending"

        return {
            "setup_type": setup_type,
            "location_type": location_type,
            "base_quality": base_quality,
            "retest_quality": retest_quality,
            "note": note,
        }

    @staticmethod
    def _read_relative_context(*, candidate: dict[str, Any], ohlcv_context: dict[str, Any]) -> dict[str, str | float]:
        rs_score = float(candidate.get("rs_score", 0.0) or 0.0)
        sector_state = str(candidate.get("sector_state", ""))
        relative_note = "supportive"
        if sector_state == "WATCH":
            relative_note = "mixed"
        if rs_score < 65:
            relative_note = "early"
        return {
            "sector_state": sector_state,
            "rs_score": rs_score,
            "relative_note": relative_note,
        }

    @staticmethod
    def _trend_quality_score(
        *,
        candle: dict[str, str],
        structure: dict[str, str],
        relative: dict[str, str | float],
    ) -> float:
        score = 5.5
        if candle["signal"] in {"bullish_momentum", "constructive"}:
            score += 1.0
        if structure["base_quality"] in {"tight_base", "acceptable"}:
            score += 1.0
        if structure["setup_type"] in {"base_breakout", "continuation_break"}:
            score += 0.8
        if float(relative["rs_score"]) >= 75:
            score += 0.9
        elif float(relative["rs_score"]) >= 65:
            score += 0.4
        return round(min(score, 9.2), 1)

    @staticmethod
    def _volume_confirmation_score(*, volume: dict[str, str | float]) -> float:
        signal = str(volume["signal"])
        if signal == "expanded_confirmed":
            return 8.0
        if signal == "moderate":
            return 6.3
        if signal == "drying_up":
            return 5.6
        return 4.8

    @staticmethod
    def _setup_readiness_score(
        *,
        candle: dict[str, str],
        volume: dict[str, str | float],
        structure: dict[str, str],
        relative: dict[str, str | float],
    ) -> float:
        score = 5.4
        if structure["setup_type"] == "base_breakout":
            score += 1.4
        elif structure["setup_type"] in {"base_forming", "continuation_break"}:
            score += 0.8
        if structure["location_type"] not in {"near_resistance", "unclear"}:
            score += 0.7
        if candle["close_quality"] in {"strong_close_near_high", "acceptable"}:
            score += 0.6
        if str(volume["signal"]) == "expanded_confirmed":
            score += 0.8
        if str(relative["sector_state"]) in {"ACTIVE", "HOT"}:
            score += 0.8
        elif str(relative["sector_state"]) == "WATCH":
            score += 0.3
        return round(min(score, 9.1), 1)

    @staticmethod
    def _why_in(
        *,
        candidate: dict[str, Any],
        candle: dict[str, str],
        volume: dict[str, str | float],
        structure: dict[str, str],
        relative: dict[str, str | float],
    ) -> list[str]:
        reasons: list[str] = []
        if candle["close_quality"] == "strong_close_near_high":
            reasons.append("strong_close")
        elif candle["signal"] in {"bullish_momentum", "constructive"}:
            reasons.append("constructive_candle")
        if str(volume["signal"]) == "expanded_confirmed":
            reasons.append("volume_expansion")
        elif str(volume["signal"]) == "moderate":
            reasons.append("volume_ok")
        if structure["setup_type"] == "base_breakout":
            reasons.append("breakout_structure")
        elif structure["base_quality"] in {"tight_base", "acceptable"}:
            reasons.append("base_ok")
        if str(relative["sector_state"]) == "ACTIVE":
            reasons.append("sector_active")
        elif str(relative["sector_state"]) == "HOT":
            reasons.append("sector_hot")
        elif str(relative["sector_state"]) == "WATCH":
            reasons.append("sector_watch")
        if float(relative["rs_score"]) >= 75:
            reasons.append("rs_supportive")
        return reasons[:4]

    @staticmethod
    def _why_not_top(
        *,
        candle: dict[str, str],
        volume: dict[str, str | float],
        structure: dict[str, str],
        relative: dict[str, str | float],
    ) -> list[str]:
        reasons: list[str] = []
        if str(volume["signal"]) not in {"expanded_confirmed", "moderate"}:
            reasons.append("needs_volume_confirmation")
        if structure["location_type"] == "near_resistance":
            reasons.append("still_under_resistance")
        if structure["base_quality"] == "loose":
            reasons.append("base_not_tight")
        if structure["retest_quality"] == "pending" and structure["setup_type"] not in {"base_breakout"}:
            reasons.append("needs_follow_through")
        if str(relative["sector_state"]) == "WATCH":
            reasons.append("sector_not_fully_confirmed")
        return reasons[:4]

    @staticmethod
    def _risk_note(
        *,
        candle: dict[str, str],
        volume: dict[str, str | float],
        structure: dict[str, str],
    ) -> list[str]:
        risks: list[str] = []
        if structure["location_type"] == "near_resistance":
            risks.append("near_short_term_resistance")
        if structure["retest_quality"] == "pending":
            risks.append("watch_follow_through_next_bar")
        if candle["signal"] == "unclear":
            risks.append("candle_confirmation_thin")
        if str(volume["signal"]) == "unclear":
            risks.append("volume_context_thin")
        return risks[:3]

    @staticmethod
    def _classify_setup(
        *,
        trend_quality_score: float,
        volume_confirmation_score: float,
        setup_readiness_score: float,
        why_not_top: list[str],
        risk_note: list[str],
        ohlcv_context: dict[str, Any],
    ) -> str:
        strong_confirmation = (
            trend_quality_score >= 7.8
            and volume_confirmation_score >= 7.0
            and setup_readiness_score >= 7.8
            and not why_not_top
        )
        if strong_confirmation:
            return "TOP"

        partial_but_valid = (
            trend_quality_score >= 6.0
            and setup_readiness_score >= 6.0
            and (
                volume_confirmation_score >= 5.5
                or (
                    volume_confirmation_score >= 4.8
                    and trend_quality_score >= 7.0
                    and setup_readiness_score >= 6.8
                )
                or bool(ohlcv_context)
            )
        )
        if partial_but_valid:
            return "WATCH"
        return "REJECT"

    @staticmethod
    def _final_score(
        *,
        classification: str,
        trend_quality_score: float,
        volume_confirmation_score: float,
        setup_readiness_score: float,
        why_not_top: list[str],
    ) -> float | None:
        if classification == "REJECT":
            return None

        weakest = min(trend_quality_score, volume_confirmation_score, setup_readiness_score)
        average = (trend_quality_score + volume_confirmation_score + setup_readiness_score) / 3.0
        summary = min(average, weakest + 0.6)
        if why_not_top:
            summary = min(summary, 7.0)
        return round(summary, 1)

    @staticmethod
    def _confidence(
        *,
        input_status: str,
        config_loaded: bool,
        top_count: int,
        watch_count: int,
        rejected_count: int,
        warning_count: int,
    ) -> float:
        if input_status == "missing" or not config_loaded:
            return 0.0
        if top_count == 0 and watch_count == 0:
            return 0.25

        confidence = 0.79 if input_status == "loaded" else 0.6
        confidence -= min(rejected_count, 3) * 0.03
        confidence -= min(warning_count, 3) * 0.05
        return max(0.18, min(confidence, 0.87))
