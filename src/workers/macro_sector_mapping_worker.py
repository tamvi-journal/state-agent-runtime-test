from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json

from workers.contracts import WorkerContractValidator


@dataclass(slots=True)
class MacroSectorMappingWorker:
    """
    Bounded macro-sector mapping worker for the thin runtime harness.

    Responsibilities:
    - receive normalized macro signals explicitly
    - load the canonical trigger map config
    - map signals into structured VN sector-bias evidence
    - preserve conflicts and weak evidence honestly

    Non-goals:
    - no raw news ingestion
    - no hidden sample fallback
    - no final user-facing report generation
    """

    config_path: str | Path = "config/macro_sector_map_v1.json"
    validator: WorkerContractValidator | None = None
    _trigger_map_cache: dict[str, Any] | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.config_path = str(self.config_path)
        if self.validator is None:
            self.validator = WorkerContractValidator()

    def run(self, *, macro_signal_payload: dict[str, Any] | None) -> dict[str, Any]:
        trace = [
            "received explicit macro-sector-mapping request",
            "using macro-sector-mapping method: normalized signals -> trigger match -> sector implications -> conservative merge",
            f"loading canonical trigger map from {self.config_path}",
        ]
        assumptions = [
            "macro signals are already normalized before entering this worker",
            "reason remains canonical to the matched trigger key",
            "config notes may explain a mapping but do not replace the canonical reason field",
        ]
        warnings: list[str] = []

        trigger_map, config_error = self._load_trigger_map()
        if config_error is not None:
            warnings.append(config_error)

        signal_data = self._extract_signal_data(macro_signal_payload=macro_signal_payload)
        input_status = signal_data["input_status"]
        scan_date = signal_data["scan_date"]
        signals = signal_data["signals"]
        trace.extend(signal_data["trace"])
        warnings.extend(signal_data["warnings"])

        matched_signals: list[dict[str, Any]] = []
        unmatched_signals: list[str] = []
        raw_bias_entries: list[dict[str, Any]] = []

        if trigger_map is not None and signals:
            for signal in signals:
                matched_trigger = self._match_trigger(signal=signal, trigger_map=trigger_map)
                if matched_trigger is None:
                    unmatched_signals.append(str(signal.get("signal_id", "unknown_signal")))
                    continue

                matched_signals.append(
                    {
                        "signal_id": str(signal.get("signal_id", "")),
                        "matched_trigger": matched_trigger["trigger_key"],
                        "direction": str(signal.get("direction", "")),
                        "confidence": str(matched_trigger.get("confidence", "unknown")),
                        "decay_days": int(matched_trigger.get("decay_days", 0)),
                    }
                )
                raw_bias_entries.extend(
                    self._expand_bias_entries(
                        signal=signal,
                        matched_trigger_key=matched_trigger["trigger_key"],
                        matched_trigger=matched_trigger,
                    )
                )
        elif trigger_map is None:
            warnings.append("macro-sector mapping could not proceed because trigger-map config was unavailable")
        elif not signals:
            warnings.append("macro-sector mapping could not proceed because explicit normalized macro signals were missing")

        vn_sector_bias, conflict_flags = self._merge_bias_entries(raw_bias_entries=raw_bias_entries)

        if unmatched_signals:
            warnings.append("one or more macro signals did not match a canonical trigger")
        if conflict_flags:
            warnings.append("conflicting macro implications were preserved for one or more sectors")

        confidence = self._confidence(
            input_status=input_status,
            config_loaded=trigger_map is not None,
            matched_count=len(matched_signals),
            conflict_count=len(conflict_flags),
            warning_count=len(warnings),
        )

        payload = {
            "worker_name": "macro_sector_mapping_worker",
            "result": {
                "task_type": "macro_sector_mapping",
                "input_status": input_status if trigger_map is not None else "missing",
                "scan_date": scan_date,
                "matched_signals": matched_signals,
                "unmatched_signals": unmatched_signals,
                "vn_sector_bias": vn_sector_bias,
                "conflict_flags": conflict_flags,
                "config_source": self.config_path,
            },
            "confidence": confidence,
            "assumptions": assumptions,
            "warnings": warnings,
            "trace": trace + ["macro sector mapping worker packaged structured sector-bias evidence for the brain"],
            "proposed_memory_update": None,
        }
        return self.validator.validate(payload)

    def _load_trigger_map(self) -> tuple[dict[str, Any] | None, str | None]:
        if self._trigger_map_cache is not None:
            return self._trigger_map_cache, None

        path = Path(self.config_path)
        if not path.exists():
            return None, "canonical macro trigger map does not exist"

        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None, "canonical macro trigger map could not be parsed"

        if not isinstance(loaded, dict) or not loaded:
            return None, "canonical macro trigger map was empty or invalid"

        self._trigger_map_cache = loaded
        return loaded, None

    @staticmethod
    def _extract_signal_data(*, macro_signal_payload: dict[str, Any] | None) -> dict[str, Any]:
        trace: list[str] = []
        warnings: list[str] = []
        if not isinstance(macro_signal_payload, dict):
            return {
                "input_status": "missing",
                "scan_date": "",
                "signals": [],
                "trace": trace + ["no explicit macro signal payload was supplied to the worker"],
                "warnings": warnings,
            }

        payload_data = macro_signal_payload.get("data", macro_signal_payload)
        if not isinstance(payload_data, dict):
            return {
                "input_status": "missing",
                "scan_date": "",
                "signals": [],
                "trace": trace + ["macro signal payload was present but did not contain a structured data object"],
                "warnings": warnings,
            }

        raw_signals = payload_data.get("global_signals", [])
        if not isinstance(raw_signals, list):
            return {
                "input_status": "missing",
                "scan_date": str(payload_data.get("scan_date", "")),
                "signals": [],
                "trace": trace + ["macro signal payload did not contain a valid global_signals list"],
                "warnings": warnings,
            }

        valid_signals: list[dict[str, Any]] = []
        partial = False
        for signal in raw_signals:
            if not isinstance(signal, dict):
                partial = True
                continue
            if not signal.get("signal_id") or not signal.get("theme") or not signal.get("direction"):
                partial = True
                continue
            valid_signals.append(signal)

        if not valid_signals:
            input_status = "missing"
        elif partial:
            input_status = "partial"
        else:
            input_status = "loaded"

        if partial:
            warnings.append("one or more normalized macro signals were incomplete and were skipped")

        return {
            "input_status": input_status,
            "scan_date": str(payload_data.get("scan_date", "")),
            "signals": valid_signals,
            "trace": trace + [f"received {len(valid_signals)} usable normalized macro signals"],
            "warnings": warnings,
        }

    @staticmethod
    def _match_trigger(*, signal: dict[str, Any], trigger_map: dict[str, Any]) -> dict[str, Any] | None:
        theme = str(signal.get("theme", "")).strip().lower()
        headline = str(signal.get("headline", "")).strip().lower()
        summary = str(signal.get("summary", "")).strip().lower()
        tags = [str(tag).strip().lower() for tag in signal.get("tags", []) if str(tag).strip()]
        direction = str(signal.get("direction", "")).strip().lower()
        haystack = " ".join([theme, headline, summary, " ".join(tags)])

        keyword_map = [
            ("hormuz_risk", lambda: "hormuz" in haystack or ("middle_east" in haystack and "oil" in haystack)),
            ("oil_up", lambda: theme == "oil" and direction == "positive"),
            ("oil_down", lambda: theme == "oil" and direction == "negative"),
            ("china_stimulus", lambda: theme == "china" and ("stimulus" in haystack or direction == "positive")),
            ("usd_strength", lambda: theme == "usd" and direction == "positive"),
            ("fed_dovish", lambda: theme == "fed" and ("dovish" in haystack or "rate cut" in haystack)),
            ("fed_hawkish", lambda: theme == "fed" and ("hawkish" in haystack or "higher for longer" in haystack)),
            ("commodity_up", lambda: "commodity" in haystack and direction == "positive"),
            ("commodity_down", lambda: "commodity" in haystack and direction == "negative"),
            ("global_risk_on", lambda: "risk_on" in haystack or ("risk" in haystack and direction == "positive")),
            ("global_risk_off", lambda: "risk_off" in haystack or ("risk" in haystack and direction == "negative")),
            ("vnd_depreciation", lambda: "vnd" in haystack and ("depreciation" in haystack or direction == "negative")),
            ("china_property_crisis", lambda: "china" in haystack and "property" in haystack and ("crisis" in haystack or direction == "negative")),
            ("gold_up", lambda: theme == "gold" and direction == "positive"),
            ("rate_cut_vn", lambda: ("rate_cut_vn" in haystack) or ("vn" in haystack and "rate cut" in haystack)),
            ("election_cycle", lambda: "election" in haystack),
            ("fdi_inflow", lambda: "fdi" in haystack and ("inflow" in haystack or direction == "positive")),
            ("export_demand_shift", lambda: "export" in haystack and ("shift" in haystack or "demand" in haystack)),
        ]

        for trigger_key, matcher in keyword_map:
            if trigger_key in trigger_map and matcher():
                trigger = trigger_map[trigger_key]
                if isinstance(trigger, dict):
                    return trigger
        return None

    @staticmethod
    def _expand_bias_entries(
        *,
        signal: dict[str, Any],
        matched_trigger_key: str,
        matched_trigger: dict[str, Any],
    ) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        signal_id = str(signal.get("signal_id", ""))
        signal_strength = float(signal.get("strength_score", 0.0) or 0.0)
        explanation = str(matched_trigger.get("notes", ""))
        confidence = str(matched_trigger.get("confidence", "unknown"))
        decay_days = int(matched_trigger.get("decay_days", 0))
        watch_stocks_map = matched_trigger.get("watch_stocks", {})

        for sector in matched_trigger.get("vn_sectors_positive", []):
            sector_key = str(sector)
            entries.append(
                {
                    "trigger_signal_id": signal_id,
                    "sector": sector_key,
                    "direction": "positive",
                    "strength_score": signal_strength,
                    "confidence": confidence,
                    "decay_days": decay_days,
                    "reason": matched_trigger_key,
                    "watch_stocks": list(watch_stocks_map.get(sector_key, [])),
                    "explanation": explanation,
                }
            )

        for sector in matched_trigger.get("vn_sectors_negative", []):
            sector_key = str(sector)
            entries.append(
                {
                    "trigger_signal_id": signal_id,
                    "sector": sector_key,
                    "direction": "negative",
                    "strength_score": signal_strength,
                    "confidence": confidence,
                    "decay_days": decay_days,
                    "reason": matched_trigger_key,
                    "watch_stocks": list(watch_stocks_map.get(sector_key, [])),
                    "explanation": explanation,
                }
            )

        return entries

    @staticmethod
    def _merge_bias_entries(
        *,
        raw_bias_entries: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        if not raw_bias_entries:
            return [], []

        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for entry in raw_bias_entries:
            key = (str(entry["sector"]), str(entry["direction"]))
            grouped.setdefault(key, []).append(entry)

        merged_entries: list[dict[str, Any]] = []
        for (sector, direction), entries in grouped.items():
            strongest = max(entries, key=lambda item: float(item.get("strength_score", 0.0)))
            merged_entries.append(
                {
                    "trigger_signal_id": strongest["trigger_signal_id"],
                    "sector": sector,
                    "direction": direction,
                    "strength_score": strongest["strength_score"],
                    "confidence": strongest["confidence"],
                    "decay_days": strongest["decay_days"],
                    "reason": strongest["reason"],
                    "watch_stocks": strongest["watch_stocks"],
                    "explanation": strongest.get("explanation", ""),
                    "supporting_trigger_signal_ids": sorted({str(entry["trigger_signal_id"]) for entry in entries}),
                }
            )

        conflicts: list[dict[str, Any]] = []
        sectors = sorted({entry["sector"] for entry in merged_entries})
        for sector in sectors:
            sector_entries = [entry for entry in merged_entries if entry["sector"] == sector]
            directions = sorted({str(entry["direction"]) for entry in sector_entries})
            if len(directions) > 1:
                conflicts.append(
                    {
                        "sector": sector,
                        "directions": directions,
                        "trigger_signal_ids": sorted(
                            {
                                signal_id
                                for entry in sector_entries
                                for signal_id in entry.get("supporting_trigger_signal_ids", [])
                            }
                        ),
                    }
                )

        merged_entries.sort(key=lambda item: (item["sector"], item["direction"]))
        return merged_entries, conflicts

    @staticmethod
    def _confidence(
        *,
        input_status: str,
        config_loaded: bool,
        matched_count: int,
        conflict_count: int,
        warning_count: int,
    ) -> float:
        if input_status == "missing" or not config_loaded:
            return 0.0
        if matched_count == 0:
            return 0.2

        confidence = 0.78 if input_status == "loaded" else 0.58
        confidence -= min(conflict_count, 3) * 0.08
        confidence -= min(warning_count, 3) * 0.05
        return max(0.15, min(confidence, 0.85))
