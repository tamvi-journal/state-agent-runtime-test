from __future__ import annotations

from typing import Any


class SynthesisGate:
    """
    Guards the boundary between worker evidence and final judgment.

    Responsibilities:
    - require core worker contract fields
    - reject malformed payloads
    - reject obvious authority creep patterns
    - normalize worker evidence before main-brain synthesis

    This is intentionally strict and simple for phase 1.
    """

    REQUIRED_FIELDS = {
        "worker_name",
        "result",
        "confidence",
        "assumptions",
        "warnings",
        "trace",
    }

    FORBIDDEN_TOP_LEVEL_FIELDS = {
        "final_answer",
        "final_judgment",
        "commit_memory",
        "memory_commit",
        "reading_position",
        "system_override",
    }

    def normalize(self, worker_payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(worker_payload, dict):
            raise TypeError("worker_payload must be a dict")

        missing = self.REQUIRED_FIELDS - set(worker_payload.keys())
        if missing:
            raise ValueError(f"worker_payload missing required fields: {sorted(missing)}")

        forbidden = self.FORBIDDEN_TOP_LEVEL_FIELDS & set(worker_payload.keys())
        if forbidden:
            raise ValueError(
                f"worker_payload contains forbidden authority fields: {sorted(forbidden)}"
            )

        worker_name = worker_payload["worker_name"]
        result = worker_payload["result"]
        confidence = worker_payload["confidence"]
        assumptions = worker_payload["assumptions"]
        warnings = worker_payload["warnings"]
        trace = worker_payload["trace"]
        proposed_memory_update = worker_payload.get("proposed_memory_update")

        if not isinstance(worker_name, str) or not worker_name.strip():
            raise ValueError("worker_name must be a non-empty string")

        if not isinstance(confidence, (int, float)):
            raise TypeError("confidence must be a number")
        confidence = float(confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        if not isinstance(assumptions, list) or not all(isinstance(x, str) for x in assumptions):
            raise TypeError("assumptions must be list[str]")

        if not isinstance(warnings, list) or not all(isinstance(x, str) for x in warnings):
            raise TypeError("warnings must be list[str]")

        if not isinstance(trace, list) or not all(isinstance(x, str) for x in trace):
            raise TypeError("trace must be list[str]")

        if proposed_memory_update is not None and not isinstance(proposed_memory_update, dict):
            raise TypeError("proposed_memory_update must be dict or None")

        # result may be any structured object, but raw persuasive prose is not allowed
        if isinstance(result, str):
            raise ValueError(
                "result must be structured data, not raw persuasive prose"
            )

        return {
            "worker_name": worker_name,
            "result": result,
            "confidence": confidence,
            "assumptions": assumptions,
            "warnings": warnings,
            "trace": trace,
            "proposed_memory_update": proposed_memory_update,
        }
