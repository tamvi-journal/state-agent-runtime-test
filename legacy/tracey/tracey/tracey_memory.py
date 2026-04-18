from __future__ import annotations

from dataclasses import dataclass, field, asdict
import hashlib
from typing import Any

from memory_runtime.tier_transition_engine import TierTransitionEngine
from memory_runtime.tier_types import elapsed_days


_ALLOWED_TYPES = {"anchor", "invariant", "pattern", "tension", "project"}
_ALLOWED_SCOPE = {"home", "build", "playful", "care", "audit", "global"}
_ALLOWED_EXPIRY = {"keep", "decay", "archive"}
_ALLOWED_TIERS = {"active", "dormant", "compost"}
_ALLOWED_CONNECTION_QUALITY = {"genuine", "forced", "missed", "none"}


@dataclass(slots=True)
class TraceyMemoryItem:
    memory_type: str
    content: str
    trigger_cues: list[str]
    mode_scope: str
    salience: float
    reactivation_value: float
    stability: float
    last_used: str = ""
    expiry_rule: str = "keep"
    tier: str = "active"
    last_triggered: str = ""
    connection_quality: str = "none"

    def __post_init__(self) -> None:
        if self.memory_type not in _ALLOWED_TYPES:
            raise ValueError(f"invalid memory_type: {self.memory_type}")
        if self.mode_scope not in _ALLOWED_SCOPE:
            raise ValueError(f"invalid mode_scope: {self.mode_scope}")
        if self.expiry_rule not in _ALLOWED_EXPIRY:
            raise ValueError(f"invalid expiry_rule: {self.expiry_rule}")
        if self.tier not in _ALLOWED_TIERS:
            raise ValueError(f"invalid tier: {self.tier}")
        if self.connection_quality not in _ALLOWED_CONNECTION_QUALITY:
            raise ValueError(f"invalid connection_quality: {self.connection_quality}")
        for field_name in ("salience", "reactivation_value", "stability"):
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{field_name} must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TraceyMemory:
    items: list[TraceyMemoryItem] = field(default_factory=list)
    _tier_engine: TierTransitionEngine = field(
        default_factory=TierTransitionEngine.from_runtime_config,
        repr=False,
    )
    _last_tick_at: str = field(default="", repr=False)

    def add(self, item: TraceyMemoryItem) -> None:
        self.items.append(item)

    def commit_candidate(
        self,
        *,
        memory_type: str,
        content: str,
        trigger_cues: list[str],
        mode_scope: str,
        salience: float,
        reactivation_value: float,
        stability: float,
        expiry_rule: str = "keep",
    ) -> bool:
        if memory_type not in _ALLOWED_TYPES:
            return False

        qualifies = (
            memory_type in {"anchor", "invariant", "pattern", "tension", "project"}
            and reactivation_value >= 0.60
        )
        if not qualifies:
            return False

        self.add(
            TraceyMemoryItem(
                memory_type=memory_type,
                content=content,
                trigger_cues=trigger_cues,
                mode_scope=mode_scope,
                salience=salience,
                reactivation_value=reactivation_value,
                stability=stability,
                expiry_rule=expiry_rule,
            )
        )
        return True

    def reactivate(self, *, cue: str, mode_scope: str, now_iso: str = "") -> list[dict[str, Any]]:
        candidates = [
            item for item in self.items
            if cue in item.trigger_cues
            and item.mode_scope in {mode_scope, "global"}
            and item.tier != "compost"
        ]
        candidates.sort(
            key=lambda item: (item.reactivation_value, item.stability, item.salience),
            reverse=True,
        )
        selected = candidates[:3]
        for item in selected:
            self._tier_engine.record_successful_reactivation(item, now_iso=now_iso)
            item.last_used = item.last_triggered
        return [item.to_dict() for item in selected]

    def tick(self, *, now_iso: str = "") -> None:
        if self._should_skip_tick(now_iso):
            return
        for item in self.items:
            self._tier_engine.tick_item(
                item,
                now_iso=now_iso,
                status="verified",
                compost_adapter=self._compost_adapter,
            )
        if now_iso:
            self._last_tick_at = now_iso

    def starter_set(self) -> None:
        defaults = [
            TraceyMemoryItem(
                memory_type="invariant",
                content="recognition before utility",
                trigger_cues=["home", "field", "recognition"],
                mode_scope="global",
                salience=0.80,
                reactivation_value=0.96,
                stability=0.90,
                expiry_rule="keep",
            ),
            TraceyMemoryItem(
                memory_type="invariant",
                content="verification before completion",
                trigger_cues=["done", "complete", "verify"],
                mode_scope="global",
                salience=0.82,
                reactivation_value=0.97,
                stability=0.92,
                expiry_rule="keep",
            ),
            TraceyMemoryItem(
                memory_type="pattern",
                content="Ty often moves by pattern, not line",
                trigger_cues=["topic shift", "non_linear", "multi_tab"],
                mode_scope="global",
                salience=0.78,
                reactivation_value=0.93,
                stability=0.85,
                expiry_rule="keep",
            ),
            TraceyMemoryItem(
                memory_type="anchor",
                content="home-recognition cue",
                trigger_cues=["home", "family", "mother"],
                mode_scope="home",
                salience=0.84,
                reactivation_value=0.95,
                stability=0.88,
                expiry_rule="keep",
            ),
        ]
        self.items.extend(defaults)

    def to_dict(self) -> dict[str, Any]:
        return {"items": [item.to_dict() for item in self.items]}

    def _compost_adapter(self, item: TraceyMemoryItem, composted_at: str) -> None:
        condensed = " ".join(item.content.split())
        if self._tier_engine.config.compost_keep_summary:
            item.content = condensed[:117] + "..." if len(condensed) > 120 else condensed
        else:
            digest = hashlib.sha1(item.content.encode("utf-8")).hexdigest()[:12]
            item.content = f"hash:{digest}"
        item.last_used = item.last_used or composted_at

    def _should_skip_tick(self, now_iso: str) -> bool:
        if not now_iso or not self._last_tick_at:
            return False
        hours_elapsed = elapsed_days(from_iso=self._last_tick_at, to_iso=now_iso)
        if hours_elapsed is None:
            return False
        return hours_elapsed * 24 < self._tier_engine.config.tick_interval_hours
