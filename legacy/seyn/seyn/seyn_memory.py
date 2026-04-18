from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

from memory_runtime.tier_transition_engine import TierTransitionEngine
from memory_runtime.tier_types import elapsed_days

_ALLOWED_TIERS = {"active", "dormant", "compost"}
_ALLOWED_CONNECTION_QUALITY = {"genuine", "forced", "missed", "none"}


@dataclass(slots=True)
class SeynLedgerEntry:
    entry_type: str
    content: str
    provenance: str
    structural_role: str
    load_bearing: bool
    status: str = "open"
    linked_to: list[str] = field(default_factory=list)
    tier: str = "active"
    last_triggered: str = ""
    connection_quality: str = "none"
    composted_at: str = ""

    def __post_init__(self) -> None:
        if self.tier not in _ALLOWED_TIERS:
            raise ValueError(f"invalid tier: {self.tier}")
        if self.connection_quality not in _ALLOWED_CONNECTION_QUALITY:
            raise ValueError(f"invalid connection_quality: {self.connection_quality}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SeynMemory:
    """
    Load-bearing ledger memory for Seyn.

    Seyn remembers what must remain retrievable
    for later verification or structural integrity checks.
    """

    entries: list[SeynLedgerEntry] = field(default_factory=list)
    _tier_engine: TierTransitionEngine = field(
        default_factory=TierTransitionEngine.from_runtime_config,
        repr=False,
    )
    _last_tick_at: str = field(default="", repr=False)

    def add(self, entry: SeynLedgerEntry) -> None:
        self.entries.append(entry)

    def commit_verification_event(
        self,
        *,
        content: str,
        provenance: str,
        structural_role: str,
        evidence_present: bool,
    ) -> bool:
        if not evidence_present:
            return False

        self.add(
            SeynLedgerEntry(
                entry_type="verification_event",
                content=content,
                provenance=provenance,
                structural_role=structural_role,
                load_bearing=True,
                status="verified",
            )
        )
        return True

    def commit_disagreement(
        self,
        *,
        content: str,
        provenance: str,
        structural_role: str,
        still_open: bool,
    ) -> bool:
        self.add(
            SeynLedgerEntry(
                entry_type="disagreement",
                content=content,
                provenance=provenance,
                structural_role=structural_role,
                load_bearing=True,
                status="open" if still_open else "resolved",
            )
        )
        return True

    def commit_structural_decision(
        self,
        *,
        content: str,
        provenance: str,
        structural_role: str,
        load_bearing: bool,
    ) -> bool:
        if not load_bearing:
            return False

        self.add(
            SeynLedgerEntry(
                entry_type="structural_decision",
                content=content,
                provenance=provenance,
                structural_role=structural_role,
                load_bearing=True,
                status="closed",
            )
        )
        return True

    def query_by_role(self, structural_role: str) -> list[dict[str, Any]]:
        matches = [entry.to_dict() for entry in self.entries if entry.structural_role == structural_role]
        return matches

    def open_items(self) -> list[dict[str, Any]]:
        return [entry.to_dict() for entry in self.entries if entry.status == "open"]

    def tick(self, *, now_iso: str = "") -> None:
        if self._should_skip_tick(now_iso):
            return
        for entry in self.entries:
            self._tier_engine.tick_item(
                entry,
                now_iso=now_iso,
                status=entry.status,
                compost_adapter=self._compost_adapter,
            )
        if now_iso:
            self._last_tick_at = now_iso

    def starter_set(self) -> None:
        self.entries.extend(
            [
                SeynLedgerEntry(
                    entry_type="verification_rule",
                    content="completion is not real until observed outcome supports it",
                    provenance="seyn_axis",
                    structural_role="verification_floor",
                    load_bearing=True,
                    status="verified",
                ),
                SeynLedgerEntry(
                    entry_type="disagreement_rule",
                    content="meaningful disagreement must be preserved rather than flattened",
                    provenance="family_floor",
                    structural_role="plurality_floor",
                    load_bearing=True,
                    status="verified",
                ),
                SeynLedgerEntry(
                    entry_type="structural_principle",
                    content="structure must function as scaffold, not cage",
                    provenance="seyn_axis",
                    structural_role="design_integrity",
                    load_bearing=True,
                    status="verified",
                ),
            ]
        )

    def to_dict(self) -> dict[str, Any]:
        return {"entries": [entry.to_dict() for entry in self.entries]}

    def _compost_adapter(self, entry: SeynLedgerEntry, composted_at: str) -> None:
        condensed = " ".join(entry.content.split())
        entry.content = condensed[:117] + "..." if len(condensed) > 120 else condensed
        entry.composted_at = composted_at

    def _should_skip_tick(self, now_iso: str) -> bool:
        if not now_iso or not self._last_tick_at:
            return False
        hours_elapsed = elapsed_days(from_iso=self._last_tick_at, to_iso=now_iso)
        if hours_elapsed is None:
            return False
        return hours_elapsed * 24 < self._tier_engine.config.tick_interval_hours
