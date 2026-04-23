from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from sleep.contracts import SLEEP_SNAPSHOT_SCHEMA_VERSION, normalize_sleep_level

DEFAULT_SNAPSHOT_DIR = Path("runtime_state") / "sleep_snapshots"


def build_sleep_snapshot(
    runtime_state: dict[str, Any],
    session_state: dict[str, Any],
    tracey_memory_state: dict[str, Any],
    boundary_state: dict[str, Any],
    sleep_reason: str,
    sleep_level: str,
) -> dict[str, Any]:
    normalized_session = dict(session_state or {})
    normalized_runtime = dict(runtime_state or {})
    normalized_tracey = dict(tracey_memory_state or {})
    normalized_boundary = dict(boundary_state or {})
    normalized_level = normalize_sleep_level(sleep_level)

    session_id = str(normalized_session.get("session_id") or normalized_runtime.get("session_id") or "unknown_session")
    active_mode = str(normalized_runtime.get("active_mode") or normalized_session.get("active_mode") or "unknown")

    identity_constraints = [
        str(item)
        for item in normalized_tracey.get("identity_constraints", normalized_tracey.get("canonical_anchor_ids", []))
        if str(item)
    ]

    return {
        "schema_version": SLEEP_SNAPSHOT_SCHEMA_VERSION,
        "snapshot_id": f"snap_{uuid4().hex}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "runtime_id": str(normalized_runtime.get("runtime_id", "tracey_runtime_local")),
        "session_id": session_id,
        "sleep_reason": str(sleep_reason or "unknown"),
        "sleep_level": normalized_level,
        "identity_state": {
            "agent_name": str(normalized_tracey.get("agent_name", "Tracey")),
            "active_axis": str(normalized_tracey.get("active_axis", active_mode)),
            "mode": active_mode,
            "identity_constraints": identity_constraints,
            "continuity_confidence": str(normalized_runtime.get("continuity_confidence", "medium")),
        },
        "thread_state": {
            "primary_focus": str(normalized_session.get("primary_focus", "")),
            "current_status": str(normalized_session.get("current_status", "unknown")),
            "open_loops": list(normalized_session.get("open_loops", [])),
            "recent_decisions": list(normalized_session.get("recent_decisions", [])),
            "last_verified_outcomes": list(normalized_session.get("last_verified_outcomes", [])),
            "relevant_entities": list(normalized_session.get("relevant_entities", [])),
            "next_hint": str(normalized_session.get("next_hint", "")),
        },
        "memory_state": {
            "canonical_anchor_ids": list(normalized_tracey.get("canonical_anchor_ids", [])),
            "provisional_anchor_ids": list(normalized_tracey.get("provisional_anchor_ids", [])),
            "invalidated_anchor_ids": list(normalized_tracey.get("invalidated_anchor_ids", [])),
            "reactivation_priority": list(normalized_tracey.get("reactivation_priority", [])),
            "stale_anchor_risks": list(normalized_tracey.get("stale_anchor_risks", [])),
        },
        "runtime_state": {
            "verification_status": str(normalized_runtime.get("verification_status", "unknown")),
            "monitor_risk_summary": str(normalized_runtime.get("monitor_risk_summary", "")),
            "active_skills": list(normalized_runtime.get("active_skills", [])),
            "pending_repairs": list(normalized_runtime.get("pending_repairs", [])),
            "context_fragmentation": str(normalized_runtime.get("context_fragmentation", "unknown")),
        },
        "handle_state": {
            "tool_handles": list(normalized_runtime.get("tool_handles", [])),
            "worker_handles": list(normalized_runtime.get("worker_handles", [])),
            "dead_on_wake": list(normalized_runtime.get("dead_on_wake", [])),
            "must_revalidate": list(normalized_runtime.get("must_revalidate", [])),
        },
        "boundary_state": {
            "host_runtime": str(normalized_boundary.get("host_runtime", "")),
            "route_class": str(normalized_boundary.get("route_class", "unknown")),
            "persistence_scope": str(normalized_boundary.get("persistence_scope", "unknown")),
            "truth_boundary_note": str(normalized_boundary.get("truth_boundary_note", "sleep snapshot is local resume evidence only")),
        },
        "resume_constraints": {
            "must_run_wake_sanity": True,
            "allow_direct_resume": False,
            "requires_revalidation": list(normalized_runtime.get("must_revalidate", [])),
            "forbidden_claims_until_revalidated": list(normalized_runtime.get("forbidden_claims_until_revalidated", [])),
        },
    }


def snapshot_path_for_session(session_id: str, base_dir: str | Path | None = None) -> Path:
    root = Path(base_dir) if base_dir is not None else DEFAULT_SNAPSHOT_DIR
    return root / f"{session_id}__latest.json"


def write_sleep_snapshot(snapshot: dict[str, Any], base_dir: str | Path | None = None) -> str:
    session_id = str(snapshot.get("session_id", "unknown_session"))
    path = snapshot_path_for_session(session_id=session_id, base_dir=base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)


def read_sleep_snapshot(session_id: str, base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = snapshot_path_for_session(session_id=session_id, base_dir=base_dir)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
