from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .payload_contracts import (
    CONTRACT_SCHEMA_VERSION,
    ContractValidationError,
    validate_error_response,
    validate_success_response,
)
from .session_roundtrip_store import SessionRoundtripStore


@dataclass(slots=True)
class OpenClawWrapper:
    python_executable: str = sys.executable or "python"
    module_name: str = "src.integration.openclaw_entrypoint"
    default_store_dir: Path = Path("tests/runtime_memory/session_roundtrip")

    def build_payload(
        self,
        *,
        request_id: str,
        request_text: str,
        session: dict[str, Any] | None = None,
        host_metadata: dict[str, Any] | None = None,
        kernel_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "schema_version": CONTRACT_SCHEMA_VERSION,
            "request_id": str(request_id),
            "request_text": str(request_text),
            "session": dict(session or {}),
            "host_metadata": dict(host_metadata or {}),
            "kernel_options": dict(kernel_options or {}),
        }

    def invoke_subprocess(self, payload: dict[str, Any], *, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
        serialized = json.dumps(payload, ensure_ascii=True)
        return subprocess.run(
            [self.python_executable, "-m", self.module_name],
            input=serialized,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=False,
        )

    def parse_response(self, completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
        if completed.returncode != 0:
            message = (completed.stderr or completed.stdout or "").strip() or "wrapper subprocess invocation failed"
            raise RuntimeError(f"entrypoint process failed with exit code {completed.returncode}: {message}")

        try:
            payload = json.loads(completed.stdout.lstrip("\ufeff"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"entrypoint returned invalid JSON: {exc.msg}") from exc

        if not isinstance(payload, dict):
            raise RuntimeError("entrypoint returned non-object JSON")

        status = payload.get("status")
        if status == "ok":
            return validate_success_response(payload)
        if status == "error":
            return validate_error_response(payload)
        raise ContractValidationError("entrypoint response has invalid status")

    def invoke(
        self,
        *,
        request_id: str,
        request_text: str,
        session: dict[str, Any] | None = None,
        session_id: str | None = None,
        host_metadata: dict[str, Any] | None = None,
        kernel_options: dict[str, Any] | None = None,
        persist_roundtrip: bool = False,
        store_dir: str | None = None,
        cwd: str | None = None,
    ) -> dict[str, Any]:
        merged_session = dict(session or {})
        store: SessionRoundtripStore | None = None
        if persist_roundtrip and session_id:
            store = self._build_store(store_dir=store_dir)
            stored_snapshot = store.load_snapshot(session_id)
            merged_session = self._build_session_from_snapshot(
                session_id=session_id,
                stored_snapshot=stored_snapshot,
                explicit_session=merged_session,
            )

        payload = self.build_payload(
            request_id=request_id,
            request_text=request_text,
            session=merged_session,
            host_metadata=host_metadata,
            kernel_options=kernel_options,
        )
        completed = self.invoke_subprocess(payload, cwd=cwd)
        response = self.parse_response(completed)
        if store is not None:
            self._maybe_persist_roundtrip(
                store=store,
                session_id=session_id,
                response=response,
            )
        return response

    def load_session_snapshot(self, session_id: str, *, store_dir: str | None = None) -> dict[str, Any] | None:
        return self._build_store(store_dir=store_dir).load_snapshot(session_id)

    def _build_store(self, *, store_dir: str | None) -> SessionRoundtripStore:
        root_dir = Path(store_dir) if store_dir else self.default_store_dir
        return SessionRoundtripStore(root_dir=root_dir)

    @staticmethod
    def _build_session_from_snapshot(
        *,
        session_id: str,
        stored_snapshot: dict[str, Any] | None,
        explicit_session: dict[str, Any],
    ) -> dict[str, Any]:
        merged_session: dict[str, Any] = {}
        if isinstance(stored_snapshot, dict):
            stored_session = stored_snapshot.get("session", {})
            if isinstance(stored_session, dict):
                merged_session.update(stored_session)

        for key, value in explicit_session.items():
            if value is None:
                continue
            merged_session[key] = value

        merged_session["session_id"] = session_id
        return merged_session

    @staticmethod
    def _maybe_persist_roundtrip(
        *,
        store: SessionRoundtripStore,
        session_id: str | None,
        response: dict[str, Any],
    ) -> None:
        if not session_id:
            return
        if response.get("status") != "ok":
            return

        session_metadata = response.get("session_status_metadata")
        if not isinstance(session_metadata, dict):
            return

        required_fields = {
            "current_status",
            "primary_focus",
            "open_loops",
            "last_verified_outcomes",
            "recent_decisions",
            "relevant_entities",
            "active_skills",
            "risk_notes",
            "next_hint",
        }
        if not required_fields.issubset(session_metadata.keys()):
            return

        stored_session = dict(session_metadata)
        stored_session["session_id"] = session_id
        store.save_snapshot(
            session_id=session_id,
            session_metadata=stored_session,
            baton=response.get("baton") if isinstance(response.get("baton"), dict) else {},
            snapshot_candidates=response.get("snapshot_candidates") if isinstance(response.get("snapshot_candidates"), list) else [],
        )
