from __future__ import annotations

from pathlib import Path

from workers.macro_sector_mapping_worker import MacroSectorMappingWorker


def build_macro_payload() -> dict[str, object]:
    return {
        "data": {
            "scan_date": "2026-03-29",
            "global_signals": [
                {
                    "signal_id": "oil_001",
                    "theme": "oil",
                    "headline": "Brent rises on Middle East tension",
                    "summary": "Oil extended gains after renewed geopolitical tension.",
                    "direction": "positive",
                    "strength_score": 8.4,
                    "confidence": "high",
                    "time_horizon": "short_term",
                    "source": "Reuters",
                }
            ],
        }
    }


def test_macro_sector_mapping_worker_matches_simple_positive_case() -> None:
    worker = MacroSectorMappingWorker()
    payload = worker.run(macro_signal_payload=build_macro_payload())

    assert payload["worker_name"] == "macro_sector_mapping_worker"
    assert payload["result"]["input_status"] == "loaded"
    assert payload["result"]["matched_signals"][0]["matched_trigger"] == "oil_up"
    assert any(item["sector"] == "oil_gas" and item["direction"] == "positive" for item in payload["result"]["vn_sector_bias"])


def test_macro_sector_mapping_worker_preserves_positive_and_negative_implications() -> None:
    worker = MacroSectorMappingWorker()
    payload = worker.run(macro_signal_payload=build_macro_payload())

    sectors = {(item["sector"], item["direction"], item["reason"]) for item in payload["result"]["vn_sector_bias"]}
    assert ("oil_gas", "positive", "oil_up") in sectors
    assert ("airlines", "negative", "oil_up") in sectors
    assert all(item["reason"] == "oil_up" for item in payload["result"]["vn_sector_bias"])


def test_macro_sector_mapping_worker_does_not_invent_sectors_or_watch_stocks() -> None:
    worker = MacroSectorMappingWorker()
    payload = worker.run(macro_signal_payload=build_macro_payload())

    oil_up_entries = [item for item in payload["result"]["vn_sector_bias"] if item["reason"] == "oil_up"]
    allowed_sectors = {"oil_gas", "fertilizer", "airlines", "transport", "plastics"}
    allowed_watch_stocks = {
        "oil_gas": {"PVD", "PVS", "BSR", "OIL"},
        "fertilizer": {"DPM", "DCM", "LAS", "DDV"},
        "airlines": {"HVN", "VJC"},
        "transport": {"HAH", "GMD", "VSC"},
        "plastics": {"BMP", "NTP"},
    }

    assert oil_up_entries
    for entry in oil_up_entries:
        assert entry["sector"] in allowed_sectors
        assert set(entry["watch_stocks"]).issubset(allowed_watch_stocks[entry["sector"]])


def test_macro_sector_mapping_worker_preserves_conflict_honestly() -> None:
    worker = MacroSectorMappingWorker()
    payload = worker.run(
        macro_signal_payload={
            "data": {
                "scan_date": "2026-03-29",
                "global_signals": [
                    {
                        "signal_id": "oil_up_001",
                        "theme": "oil",
                        "headline": "Brent rises",
                        "summary": "Oil moved higher.",
                        "direction": "positive",
                        "strength_score": 8.0,
                        "confidence": "high",
                        "time_horizon": "short_term",
                        "source": "Reuters",
                    },
                    {
                        "signal_id": "oil_down_001",
                        "theme": "oil",
                        "headline": "Crude falls after demand concern",
                        "summary": "Oil moved lower.",
                        "direction": "negative",
                        "strength_score": 7.2,
                        "confidence": "medium",
                        "time_horizon": "short_term",
                        "source": "Reuters",
                    },
                ],
            }
        }
    )

    assert any(flag["sector"] == "oil_gas" for flag in payload["result"]["conflict_flags"])
    assert any(flag["sector"] == "airlines" for flag in payload["result"]["conflict_flags"])


def test_macro_sector_mapping_worker_is_honest_when_input_missing() -> None:
    worker = MacroSectorMappingWorker()
    payload = worker.run(macro_signal_payload=None)

    assert payload["result"]["input_status"] == "missing"
    assert payload["result"]["matched_signals"] == []
    assert payload["result"]["vn_sector_bias"] == []
    assert payload["confidence"] == 0.0


def test_macro_sector_mapping_worker_is_honest_when_config_missing(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing_trigger_map.json"
    worker = MacroSectorMappingWorker(config_path=missing_path)
    payload = worker.run(macro_signal_payload=build_macro_payload())

    assert payload["result"]["input_status"] == "missing"
    assert payload["result"]["matched_signals"] == []
    assert payload["result"]["vn_sector_bias"] == []
    assert payload["confidence"] == 0.0
    assert any("trigger map" in warning for warning in payload["warnings"])
