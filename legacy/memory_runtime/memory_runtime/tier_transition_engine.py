from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Callable

from memory_runtime.tier_types import (
    ConnectionQuality,
    DEFAULT_MEMORY_TIER_CONFIG,
    MemoryTier,
    MemoryTierConfig,
    elapsed_days,
    parse_iso8601,
    utc_now_iso,
)


CompostAdapter = Callable[[Any, str], None]


@dataclass(slots=True)
class TransitionResult:
    changed: bool
    final_tier: MemoryTier
    composted: bool = False


class TierTransitionEngine:
    def __init__(self, config: MemoryTierConfig | None = None) -> None:
        self.config = config or DEFAULT_MEMORY_TIER_CONFIG
        self._reactivation_history: dict[int, list[str]] = {}

    @classmethod
    def from_runtime_config(cls, *, config_path: str | None = None) -> "TierTransitionEngine":
        from deploy.runtime_config import load_memory_tier_config

        return cls(config=load_memory_tier_config(config_path=config_path))

    def tick_item(
        self,
        item: Any,
        *,
        now_iso: str = "",
        status: str = "verified",
        compost_adapter: CompostAdapter | None = None,
    ) -> TransitionResult:
        current_time = now_iso or utc_now_iso()
        if getattr(item, "tier", "active") == "compost":
            return TransitionResult(changed=False, final_tier="compost", composted=False)

        changed = False
        composted = False

        while True:
            next_tier = self._next_tier(
                tier=getattr(item, "tier", "active"),
                last_triggered=getattr(item, "last_triggered", ""),
                connection_quality=getattr(item, "connection_quality", "none"),
                status=status,
                now_iso=current_time,
            )
            if next_tier == getattr(item, "tier", "active"):
                break

            setattr(item, "tier", next_tier)
            changed = True

            if next_tier == "compost":
                composted = True
                if compost_adapter is not None:
                    compost_adapter(item, current_time)
                break

        return TransitionResult(
            changed=changed,
            final_tier=getattr(item, "tier", "active"),
            composted=composted,
        )

    def record_successful_reactivation(
        self,
        item: Any,
        *,
        now_iso: str = "",
        status: str = "verified",
    ) -> None:
        current_time = now_iso or utc_now_iso()
        setattr(item, "last_triggered", current_time)

        if getattr(item, "tier", "active") != "compost" and status != "open":
            setattr(item, "tier", "active")
        elif status == "open":
            setattr(item, "tier", "active")

        quality = getattr(item, "connection_quality", "none")
        if quality == "none":
            history = self._reactivation_history.setdefault(id(item), [])
            history.append(current_time)
            self._reactivation_history[id(item)] = self._prune_history(history, current_time)
            if self._eligible_for_genuine_promotion(item):
                setattr(item, "connection_quality", "genuine")

    def _next_tier(
        self,
        *,
        tier: MemoryTier,
        last_triggered: str,
        connection_quality: ConnectionQuality,
        status: str,
        now_iso: str,
    ) -> MemoryTier:
        if tier == "compost":
            return "compost"

        if status == "open":
            return "active"

        if self.config.genuine_pin_enabled and connection_quality == "genuine":
            return "active"

        elapsed = elapsed_days(from_iso=last_triggered, to_iso=now_iso)
        if elapsed is None:
            return tier

        if tier == "active" and elapsed > self.config.active_window_days:
            return "dormant"

        if (
            tier == "dormant"
            and elapsed > self.config.dormant_window_days
            and connection_quality in {"forced", "missed", "none"}
            and status in {"verified", "resolved", "closed", ""}
        ):
            return "compost"

        return tier

    def _prune_history(self, history: list[str], now_iso: str) -> list[str]:
        now_dt = parse_iso8601(now_iso)
        if now_dt is None:
            return history[-self.config.promote_reactivation_count :]

        floor = now_dt - timedelta(days=self.config.promote_window_days)
        pruned: list[str] = []
        for value in history:
            parsed = parse_iso8601(value)
            if parsed is not None and parsed >= floor:
                pruned.append(value)
        return pruned

    def _eligible_for_genuine_promotion(self, item: Any) -> bool:
        if not self.config.promote_none_to_genuine_enabled:
            return False

        quality = getattr(item, "connection_quality", "none")
        if quality != "none":
            return False

        history = self._reactivation_history.get(id(item), [])
        return len(history) >= self.config.promote_reactivation_count
