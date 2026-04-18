from __future__ import annotations

from typing import Any

from brain.synthesis_gate import SynthesisGate


class WorkerContractValidator:
    """
    Small adapter that reuses the synthesis gate contract rules.

    Purpose in phase 1:
    - validate worker payload shape early
    - keep one strict contract definition at the boundary
    """

    def __init__(self) -> None:
        self._gate = SynthesisGate()

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Validate and normalize a worker payload.

        Returns:
            normalized payload dict
        Raises:
            TypeError / ValueError if the payload is invalid
        """
        return self._gate.normalize(payload)
