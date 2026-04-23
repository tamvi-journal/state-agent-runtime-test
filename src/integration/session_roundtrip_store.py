from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_SAFE_SESSION_ID_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(slots=True)
class SessionRoundtripStore:
    root_dir: Path
    snapshot_candidate_cap: int = 3

    def load_snapshot(self, session_id: str) -> dict[str, Any] | None:
        path = self.path_for_session(session_id)
        if not path.exists():
            return None
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(loaded, dict):
            return None
        return loaded

    def save_snapshot(
        self,
        *,
        session_id: str,
        session_metadata: dict[str, Any],
        baton: dict[str, Any] | None = None,
        snapshot_candidates: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        snapshot = {
            "session_id": session_id,
            "session": self._normalize_session_metadata(session_metadata),
            "baton": self._normalize_baton(baton or {}),
            "snapshot_candidates": self._normalize_snapshot_candidates(snapshot_candidates or []),
        }
        path = self.path_for_session(session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(snapshot, ensure_ascii=True, indent=2), encoding="utf-8")
        return snapshot

    def path_for_session(self, session_id: str) -> Path:
        safe_name = self.sanitize_session_id(session_id)
        return self.root_dir / f"{safe_name}.json"

    @staticmethod
    def sanitize_session_id(session_id: str) -> str:
        cleaned = _SAFE_SESSION_ID_PATTERN.sub("_", str(session_id).strip())
        cleaned = cleaned.strip("._")
        return cleaned or "session"

    @staticmethod
    def _normalize_session_metadata(session_metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": str(session_metadata.get("session_id", "")),
            "session_kind": str(session_metadata.get("session_kind", "")),
            "primary_focus": str(session_metadata.get("primary_focus", "")),
            "current_status": str(session_metadata.get("current_status", "")),
            "open_loops": SessionRoundtripStore._coerce_str_list(session_metadata.get("open_loops", [])),
            "last_verified_outcomes": SessionRoundtripStore._coerce_str_list(session_metadata.get("last_verified_outcomes", [])),
            "recent_decisions": SessionRoundtripStore._coerce_str_list(session_metadata.get("recent_decisions", [])),
            "relevant_entities": SessionRoundtripStore._coerce_str_list(session_metadata.get("relevant_entities", [])),
            "active_skills": SessionRoundtripStore._coerce_str_list(session_metadata.get("active_skills", [])),
            "risk_notes": SessionRoundtripStore._coerce_str_list(session_metadata.get("risk_notes", [])),
            "next_hint": str(session_metadata.get("next_hint", "")),
        }

    @staticmethod
    def _normalize_baton(baton: dict[str, Any]) -> dict[str, Any]:
        return {
            "task_focus": str(baton.get("task_focus", "")),
            "active_mode": str(baton.get("active_mode", "")),
            "open_loops": SessionRoundtripStore._coerce_str_list(baton.get("open_loops", [])),
            "verification_status": str(baton.get("verification_status", "")),
            "next_hint": str(baton.get("next_hint", "")),
        }

    def _normalize_snapshot_candidates(self, snapshot_candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for item in snapshot_candidates[: self.snapshot_candidate_cap]:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "candidate_type": str(item.get("candidate_type", "")),
                    "task_focus": str(item.get("task_focus", "")),
                    "verification_status": str(item.get("verification_status", "")),
                    "next_hint": str(item.get("next_hint", "")),
                }
            )
        return normalized

    @staticmethod
    def _coerce_str_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value if isinstance(item, str) and item]
