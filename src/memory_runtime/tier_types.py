from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal


MemoryTier = Literal["active", "dormant", "compost"]
ConnectionQuality = Literal["genuine", "forced", "missed", "none"]


@dataclass(slots=True)
class MemoryTierConfig:
    active_window_days: int = 30
    dormant_window_days: int = 180
    genuine_pin_enabled: bool = True
    compost_keep_summary: bool = True
    tick_interval_hours: int = 24
    promote_none_to_genuine_enabled: bool = True
    promote_reactivation_count: int = 3
    promote_window_days: int = 14


DEFAULT_MEMORY_TIER_CONFIG = MemoryTierConfig()


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso8601(value: str) -> datetime | None:
    if not value:
        return None

    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def elapsed_days(*, from_iso: str, to_iso: str) -> float | None:
    start = parse_iso8601(from_iso)
    end = parse_iso8601(to_iso)
    if start is None or end is None:
        return None
    return (end - start).total_seconds() / 86400.0

