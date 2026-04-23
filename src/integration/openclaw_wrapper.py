from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

from .payload_contracts import (
    CONTRACT_SCHEMA_VERSION,
    ContractValidationError,
    validate_error_response,
    validate_success_response,
)


@dataclass(slots=True)
class OpenClawWrapper:
    python_executable: str = sys.executable or "python"
    module_name: str = "src.integration.openclaw_entrypoint"

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
        host_metadata: dict[str, Any] | None = None,
        kernel_options: dict[str, Any] | None = None,
        cwd: str | None = None,
    ) -> dict[str, Any]:
        payload = self.build_payload(
            request_id=request_id,
            request_text=request_text,
            session=session,
            host_metadata=host_metadata,
            kernel_options=kernel_options,
        )
        completed = self.invoke_subprocess(payload, cwd=cwd)
        return self.parse_response(completed)
