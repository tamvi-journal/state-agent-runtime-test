from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json

from workers.contracts import WorkerContractValidator


@dataclass(slots=True)
class SectorFlowWorker:
    """
    Bounded sector-flow worker for the thin runtime harness.

    Responsibilities:
    - receive explicit sector metric input
    - optionally receive explicit macro sector-bias evidence
    - load canonical state rules and sector universe config
    - classify sector states conservatively and package evidence

    Non-goals:
    - no hidden sample fallback
    - no raw market-data ingestion
    - no final user-facing report generation
    """

    state_rules_path: str | Path = "config/sector_state_rules_v1.json"
    sector_universe_path: str | Path = "config/sector_universe_v1.json"
    validator: WorkerContractValidator | None = None
    _state_rules_cache: dict[str, Any] | None = field(default=None, init=False, repr=False)
    _sector_universe_cache: dict[str, Any] | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.state_rules_path = str(self.state_rules_path)
        self.sector_universe_path = str(self.sector_universe_path)
        if self.validator is None:
            self.validator = WorkerContractValidator()

    def run(
        self,
        *,
        sector_flow_payload: dict[str, Any] | None,
        macro_sector_bias_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        trace = [
            "received explicit sector-flow request",
            "using sector-flow-state method: metrics first -> optional macro comparison -> canonical state resolution -> overlays/conflicts",
            f"loading canonical state rules from {self.state_rules_path}",
            f"loading canonical sector universe from {self.sector_universe_path}",
        ]
        assumptions = [
            "sector metrics are supplied explicitly to this worker",
            "macro sector-bias input is optional supporting evidence, not a substitute for real flow metrics",
            "WEAKENING remains a first-class state outcome when deterioration evidence is strong",
        ]
        warnings: list[str] = []

        state_rules, state_rules_error = self._load_json_config(
            path_str=self.state_rules_path,
            cache_name="_state_rules_cache",
            missing_message="canonical sector state rules do not exist",
            invalid_message="canonical sector state rules were empty or invalid",
            parse_message="canonical sector state rules could not be parsed",
        )
        if state_rules_error is not None:
            warnings.append(state_rules_error)

        sector_universe, sector_universe_error = self._load_json_config(
            path_str=self.sector_universe_path,
            cache_name="_sector_universe_cache",
            missing_message="canonical sector universe does not exist",
            invalid_message="canonical sector universe was empty or invalid",
            parse_message="canonical sector universe could not be parsed",
        )
        if sector_universe_error is not None:
            warnings.append(sector_universe_error)

        enabled_sectors = self._enabled_sectors(sector_universe)

        metric_data = self._extract_sector_metrics(sector_flow_payload=sector_flow_payload)
        input_status = metric_data["input_status"]
        benchmark = metric_data["benchmark"]
        sector_metrics = metric_data["sector_metrics"]
        trace.extend(metric_data["trace"])
        warnings.extend(metric_data["warnings"])

        macro_bias_map, macro_warnings = self._extract_macro_bias_map(
            macro_sector_bias_payload=macro_sector_bias_payload,
            enabled_sectors=enabled_sectors,
        )
        warnings.extend(macro_warnings)
        if macro_bias_map:
            trace.append(f"received explicit macro sector-bias evidence for {len(macro_bias_map)} sectors")
        else:
            trace.append("no explicit macro sector-bias evidence was supplied")

        sector_flow_board: list[dict[str, Any]] = []
        unclassified_sectors: list[dict[str, Any]] = []
        conflict_flags: list[dict[str, Any]] = []

        classification_order = self._classification_order(state_rules)
        tie_break_notes = self._tie_break_notes(state_rules)
        late_entry_overlay = self._late_entry_overlay(state_rules)

        if state_rules is not None and sector_universe is not None and sector_metrics:
            for metric in sector_metrics:
                sector = str(metric.get("sector", ""))
                if sector not in enabled_sectors:
                    unclassified_sectors.append(
                        {
                            "sector": sector,
                            "reason": "sector_not_in_canonical_universe",
                        }
                    )
                    continue

                macro_entries = macro_bias_map.get(sector, [])
                evaluation = self._evaluate_sector(
                    metric=metric,
                    macro_entries=macro_entries,
                    state_rules=state_rules,
                    classification_order=classification_order,
                    tie_break_notes=tie_break_notes,
                    late_entry_overlay=late_entry_overlay,
                )
                if evaluation["board_entry"] is not None:
                    sector_flow_board.append(evaluation["board_entry"])
                if evaluation["unclassified"] is not None:
                    unclassified_sectors.append(evaluation["unclassified"])
                conflict_flags.extend(evaluation["conflict_flags"])
        elif state_rules is None or sector_universe is None:
            warnings.append("sector-flow classification could not proceed because canonical config was unavailable")
        elif not sector_metrics:
            warnings.append("sector-flow classification could not proceed because explicit sector metrics were missing")

        if unclassified_sectors:
            warnings.append("one or more sectors were excluded because they are not in the canonical enabled universe")
        if conflict_flags:
            warnings.append("macro-flow conflicts were preserved for one or more sectors")

        confidence = self._confidence(
            input_status=input_status,
            config_loaded=state_rules is not None and sector_universe is not None,
            classified_count=len(sector_flow_board),
            unclassified_count=len(unclassified_sectors),
            conflict_count=len(conflict_flags),
            warning_count=len(warnings),
        )

        payload = {
            "worker_name": "sector_flow_worker",
            "result": {
                "task_type": "sector_flow",
                "input_status": input_status if state_rules is not None and sector_universe is not None else "missing",
                "benchmark": benchmark,
                "sector_flow_board": sector_flow_board,
                "unclassified_sectors": unclassified_sectors,
                "conflict_flags": conflict_flags,
                "config_source": {
                    "state_rules": self.state_rules_path,
                    "sector_universe": self.sector_universe_path,
                },
            },
            "confidence": confidence,
            "assumptions": assumptions,
            "warnings": warnings,
            "trace": trace + ["sector flow worker packaged structured sector-state evidence for the brain"],
            "proposed_memory_update": None,
        }
        return self.validator.validate(payload)

    def _load_json_config(
        self,
        *,
        path_str: str,
        cache_name: str,
        missing_message: str,
        invalid_message: str,
        parse_message: str,
    ) -> tuple[dict[str, Any] | None, str | None]:
        cached = getattr(self, cache_name)
        if cached is not None:
            return cached, None

        path = Path(path_str)
        if not path.exists():
            return None, missing_message

        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None, parse_message

        if not isinstance(loaded, dict) or not loaded:
            return None, invalid_message

        setattr(self, cache_name, loaded)
        return loaded, None

    @staticmethod
    def _enabled_sectors(sector_universe: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
        if not isinstance(sector_universe, dict):
            return {}

        enabled: dict[str, dict[str, Any]] = {}
        for item in sector_universe.get("sectors", []):
            if not isinstance(item, dict):
                continue
            sector_key = str(item.get("sector_key", ""))
            if sector_key and bool(item.get("enabled", False)):
                enabled[sector_key] = item
        return enabled

    @staticmethod
    def _extract_sector_metrics(*, sector_flow_payload: dict[str, Any] | None) -> dict[str, Any]:
        trace: list[str] = []
        warnings: list[str] = []
        if not isinstance(sector_flow_payload, dict):
            return {
                "input_status": "missing",
                "benchmark": None,
                "sector_metrics": [],
                "trace": trace + ["no explicit sector metric payload was supplied to the worker"],
                "warnings": warnings,
            }

        payload_data = sector_flow_payload.get("data", sector_flow_payload)
        if not isinstance(payload_data, dict):
            return {
                "input_status": "missing",
                "benchmark": None,
                "sector_metrics": [],
                "trace": trace + ["sector metric payload was present but did not contain a structured data object"],
                "warnings": warnings,
            }

        raw_metrics = payload_data.get("sector_metrics", [])
        if not isinstance(raw_metrics, list):
            return {
                "input_status": "missing",
                "benchmark": payload_data.get("benchmark"),
                "sector_metrics": [],
                "trace": trace + ["sector metric payload did not contain a valid sector_metrics list"],
                "warnings": warnings,
            }

        required_fields = {
            "sector",
            "rs_score",
            "breadth_score",
            "volume_ratio_vs_ma20",
            "up_down_ratio",
            "leader_count",
            "breakout_count",
            "breakdown_count",
        }
        valid_metrics: list[dict[str, Any]] = []
        partial = False
        for metric in raw_metrics:
            if not isinstance(metric, dict):
                partial = True
                continue
            if any(metric.get(field) is None for field in required_fields):
                partial = True
                continue
            valid_metrics.append(metric)

        if not valid_metrics:
            input_status = "missing"
        elif partial:
            input_status = "partial"
        else:
            input_status = "loaded"

        if partial:
            warnings.append("one or more sector metric entries were incomplete and were skipped")

        return {
            "input_status": input_status,
            "benchmark": payload_data.get("benchmark"),
            "sector_metrics": valid_metrics,
            "trace": trace + [f"received {len(valid_metrics)} usable sector metric entries"],
            "warnings": warnings,
        }

    @staticmethod
    def _extract_macro_bias_map(
        *,
        macro_sector_bias_payload: dict[str, Any] | None,
        enabled_sectors: dict[str, dict[str, Any]],
    ) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
        warnings: list[str] = []
        if not isinstance(macro_sector_bias_payload, dict):
            return {}, warnings

        payload_data = macro_sector_bias_payload.get("data", macro_sector_bias_payload)
        if not isinstance(payload_data, dict):
            warnings.append("macro sector-bias payload was present but not structured")
            return {}, warnings

        raw_bias = payload_data.get("vn_sector_bias", payload_data.get("macro_sector_bias", []))
        if not isinstance(raw_bias, list):
            warnings.append("macro sector-bias payload did not contain a valid bias list")
            return {}, warnings

        grouped: dict[str, list[dict[str, Any]]] = {}
        for entry in raw_bias:
            if not isinstance(entry, dict):
                continue
            sector = str(entry.get("sector", ""))
            if sector not in enabled_sectors:
                continue
            grouped.setdefault(sector, []).append(entry)
        return grouped, warnings

    @staticmethod
    def _classification_order(state_rules: dict[str, Any] | None) -> list[str]:
        if not isinstance(state_rules, dict):
            return ["HOT", "ACTIVE", "WATCH", "WEAKENING"]
        order = state_rules.get("classification_order", [])
        if isinstance(order, list) and order:
            return [str(item) for item in order if str(item)]
        return ["HOT", "ACTIVE", "WATCH", "WEAKENING"]

    @staticmethod
    def _tie_break_notes(state_rules: dict[str, Any] | None) -> list[str]:
        if not isinstance(state_rules, dict):
            return []
        notes = state_rules.get("tie_break_notes", [])
        if isinstance(notes, list):
            return [str(note) for note in notes if str(note)]
        return []

    @staticmethod
    def _late_entry_overlay(state_rules: dict[str, Any] | None) -> dict[str, Any]:
        if not isinstance(state_rules, dict):
            return {}
        overlay = state_rules.get("late_entry_risk_overlay", {})
        return overlay if isinstance(overlay, dict) else {}

    def _evaluate_sector(
        self,
        *,
        metric: dict[str, Any],
        macro_entries: list[dict[str, Any]],
        state_rules: dict[str, Any],
        classification_order: list[str],
        tie_break_notes: list[str],
        late_entry_overlay: dict[str, Any],
    ) -> dict[str, Any]:
        states = state_rules.get("states", {})
        metric_view = self._coerce_metric(metric)

        positive_candidates = [
            state_name
            for state_name in classification_order
            if state_name in {"HOT", "ACTIVE", "WATCH"}
            and self._meets_positive_state(metric_view=metric_view, state_name=state_name, states=states)
        ]
        weakening_evidence = self._evaluate_weakening(metric_view=metric_view, states=states)

        resolved_state = self._resolve_state(
            positive_candidates=positive_candidates,
            weakening_evidence=weakening_evidence,
            classification_order=classification_order,
            tie_break_notes=tie_break_notes,
            prior_state=metric_view["prior_state"],
        )

        if not resolved_state:
            return {
                "board_entry": None,
                "unclassified": {
                    "sector": metric_view["sector"],
                    "reason": "insufficient_confirmation_for_honest_state",
                },
                "conflict_flags": [],
            }

        overlays = self._build_overlays(
            state=resolved_state,
            metric=metric,
            late_entry_overlay=late_entry_overlay,
            macro_entries=macro_entries,
        )

        macro_direction, macro_alignment, macro_conflict = self._macro_posture(
            resolved_state=resolved_state,
            metric=metric,
            macro_entries=macro_entries,
        )

        board_entry = {
            "sector": metric_view["sector"],
            "state": resolved_state,
            "direction": self._direction_for_state(resolved_state),
            "rs_score": metric_view["rs_score"],
            "volume_ratio_vs_ma20": metric_view["volume_ratio_vs_ma20"],
            "breadth_score": metric_view["breadth_score"],
            "up_down_ratio": metric_view["up_down_ratio"],
            "breakout_count": metric_view["breakout_count"],
            "breakdown_count": metric_view["breakdown_count"],
            "leader_count": metric_view["leader_count"],
            "macro_alignment": macro_alignment,
            "conflict_flag": macro_conflict,
            "overlays": overlays,
        }
        if metric.get("change_pct") is not None:
            board_entry["change_pct"] = float(metric.get("change_pct", 0.0))
        if macro_direction:
            board_entry["macro_direction"] = macro_direction
        if metric.get("flags") is not None and isinstance(metric.get("flags"), list):
            board_entry["flags"] = [str(item) for item in metric.get("flags", []) if str(item)]

        conflict_flags: list[dict[str, Any]] = []
        if macro_conflict and macro_direction:
            conflict_flags.append(
                {
                    "sector": metric_view["sector"],
                    "macro_direction": macro_direction,
                    "flow_state": resolved_state,
                    "reason": "macro_flow_conflict",
                }
            )

        return {
            "board_entry": board_entry,
            "unclassified": None,
            "conflict_flags": conflict_flags,
        }

    @staticmethod
    def _coerce_metric(metric: dict[str, Any]) -> dict[str, Any]:
        return {
            "sector": str(metric.get("sector", "")),
            "rs_score": float(metric.get("rs_score", 0.0)),
            "breadth_score": float(metric.get("breadth_score", 0.0)),
            "volume_ratio_vs_ma20": float(metric.get("volume_ratio_vs_ma20", 0.0)),
            "up_down_ratio": float(metric.get("up_down_ratio", 0.0)),
            "leader_count": int(metric.get("leader_count", 0)),
            "breakout_count": int(metric.get("breakout_count", 0)),
            "breakdown_count": int(metric.get("breakdown_count", 0)),
            "rs_score_drop_3d": float(metric.get("rs_score_drop_3d", 0.0) or 0.0),
            "prior_state": str(metric.get("prior_state", "")).upper(),
            "macro_alignment": bool(metric.get("macro_alignment", False)),
        }

    @staticmethod
    def _meets_positive_state(
        *,
        metric_view: dict[str, Any],
        state_name: str,
        states: dict[str, Any],
    ) -> bool:
        state = states.get(state_name, {})
        minimum_conditions = state.get("minimum_conditions", {})
        if not isinstance(minimum_conditions, dict):
            return False

        numeric_mapping = {
            "rs_score_min": metric_view["rs_score"],
            "breadth_score_min": metric_view["breadth_score"],
            "volume_ratio_vs_ma20_min": metric_view["volume_ratio_vs_ma20"],
            "up_down_ratio_min": metric_view["up_down_ratio"],
            "leader_count_min": metric_view["leader_count"],
            "breakout_count_min": metric_view["breakout_count"],
        }

        for rule_key, actual_value in numeric_mapping.items():
            threshold = minimum_conditions.get(rule_key)
            if threshold is None:
                continue
            if float(actual_value) < float(threshold):
                return False

        supporting_conditions_any = state.get("supporting_conditions_any", [])
        if state_name != "WATCH" or not isinstance(supporting_conditions_any, list) or not supporting_conditions_any:
            return True

        macro_alignment = bool(metric_view.get("macro_alignment", False))
        for condition in supporting_conditions_any:
            text = str(condition)
            if text == "macro_alignment == true" and macro_alignment:
                return True
            if text == "up_down_ratio >= 1.2" and metric_view["up_down_ratio"] >= 1.2:
                return True
            if text == "leader_count >= 1" and metric_view["leader_count"] >= 1:
                return True
        return False

    @staticmethod
    def _evaluate_weakening(
        *,
        metric_view: dict[str, Any],
        states: dict[str, Any],
    ) -> dict[str, Any]:
        weakening_rules = states.get("WEAKENING", {})
        triggers = weakening_rules.get("trigger_conditions_any", [])
        matched_signals: list[str] = []

        for trigger in triggers:
            text = str(trigger)
            if text == "rs_score_drop_3d >= 5" and metric_view["rs_score_drop_3d"] >= 5.0:
                matched_signals.append(text)
            elif text == "breadth_score < 5.0" and metric_view["breadth_score"] < 5.0:
                matched_signals.append(text)
            elif (
                text == "volume_ratio_vs_ma20 < 0.9 after prior ACTIVE/HOT"
                and metric_view["volume_ratio_vs_ma20"] < 0.9
                and str(metric_view.get("prior_state", "")).upper() in {"ACTIVE", "HOT"}
            ):
                matched_signals.append(text)
            elif text == "breakdown_count >= 2" and metric_view["breakdown_count"] >= 2:
                matched_signals.append(text)
            elif (
                text == "up_down_ratio < 1.0 after prior ACTIVE/HOT"
                and metric_view["up_down_ratio"] < 1.0
                and str(metric_view.get("prior_state", "")).upper() in {"ACTIVE", "HOT"}
            ):
                matched_signals.append(text)

        strong_deterioration = (
            metric_view["breakdown_count"] >= 2
            or metric_view["breadth_score"] < 5.0
            or metric_view["rs_score_drop_3d"] >= 5.0
        )
        return {
            "triggered": bool(matched_signals),
            "matched_signals": matched_signals,
            "strong_deterioration": strong_deterioration,
        }

    @staticmethod
    def _resolve_state(
        *,
        positive_candidates: list[str],
        weakening_evidence: dict[str, Any],
        classification_order: list[str],
        tie_break_notes: list[str],
        prior_state: str,
    ) -> str:
        strongest_positive = ""
        for state_name in classification_order:
            if state_name in positive_candidates:
                strongest_positive = state_name
                break

        weakening_triggered = bool(weakening_evidence.get("triggered", False))
        strong_deterioration = bool(weakening_evidence.get("strong_deterioration", False))
        prior_strong = prior_state in {"ACTIVE", "HOT"}

        if weakening_triggered and (strong_deterioration or strongest_positive in {"", "WATCH"} or prior_strong):
            return "WEAKENING"

        if strongest_positive:
            if (
                strongest_positive == "WATCH"
                and weakening_triggered
                and prior_strong
                and any("prefer WEAKENING over WATCH" in note for note in tie_break_notes)
                ):
                return "WEAKENING"
            return strongest_positive

        if weakening_triggered:
            return "WEAKENING"
        return ""

    @staticmethod
    def _build_overlays(
        *,
        state: str,
        metric: dict[str, Any],
        late_entry_overlay: dict[str, Any],
        macro_entries: list[dict[str, Any]],
    ) -> list[str]:
        overlays: list[str] = []
        if state == "HOT":
            conditions = late_entry_overlay.get("conditions", {})
            if (
                isinstance(conditions, dict)
                and str(conditions.get("state", "")) == "HOT"
                and int(metric.get("hot_streak_days", 0) or 0) >= int(conditions.get("hot_streak_days_min", 0) or 0)
            ):
                overlays.append(str(late_entry_overlay.get("output_flag", "late_entry_risk")))

        if macro_entries and state == "WEAKENING":
            overlays.append("macro_story_not_confirmed")
        return overlays

    @staticmethod
    def _macro_posture(
        *,
        resolved_state: str,
        metric: dict[str, Any],
        macro_entries: list[dict[str, Any]],
    ) -> tuple[str, bool, bool]:
        if macro_entries:
            directions = [str(entry.get("direction", "")) for entry in macro_entries if str(entry.get("direction", ""))]
            macro_direction = directions[0] if directions else ""
        else:
            macro_direction = "positive" if bool(metric.get("macro_alignment", False)) else ""

        state_direction = SectorFlowWorker._direction_for_state(resolved_state)
        macro_alignment = bool(metric.get("macro_alignment", False))
        macro_conflict = False
        if macro_direction:
            macro_alignment = macro_direction == state_direction
            macro_conflict = not macro_alignment
        return macro_direction, macro_alignment, macro_conflict

    @staticmethod
    def _direction_for_state(state: str) -> str:
        if state == "WEAKENING":
            return "negative"
        return "positive"

    @staticmethod
    def _confidence(
        *,
        input_status: str,
        config_loaded: bool,
        classified_count: int,
        unclassified_count: int,
        conflict_count: int,
        warning_count: int,
    ) -> float:
        if input_status == "missing" or not config_loaded:
            return 0.0
        if classified_count == 0:
            return 0.2

        confidence = 0.8 if input_status == "loaded" else 0.62
        confidence -= min(unclassified_count, 3) * 0.05
        confidence -= min(conflict_count, 3) * 0.06
        confidence -= min(warning_count, 3) * 0.05
        return max(0.15, min(confidence, 0.88))
