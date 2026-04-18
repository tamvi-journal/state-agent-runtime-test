from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from memory_runtime.memory_read_policy import MemoryReadPolicy
from memory_runtime.memory_write_policy import MemoryWritePolicy
from laws.memory_commit_law import MemoryCommitLaw


@dataclass(slots=True)
class ContinuityGateway:
    """
    Runtime-facing gateway between:
    - live state
    - archive memory
    - family memory
    - write-side persistence rules
    """

    read_policy: MemoryReadPolicy = field(default_factory=MemoryReadPolicy)
    write_policy: MemoryWritePolicy = field(default_factory=lambda: MemoryWritePolicy(commit_law=MemoryCommitLaw()))

    def read_access(
        self,
        *,
        task_type: str,
        active_mode: str,
        archive_needed: bool,
        family_signal_detected: bool,
    ) -> dict[str, Any]:
        return self.read_policy.decide(
            task_type=task_type,
            active_mode=active_mode,
            archive_needed=archive_needed,
            family_signal_detected=family_signal_detected,
        ).to_dict()

    def write_access(
        self,
        *,
        object_type: str,
        load_bearing: bool = False,
        verified: bool = False,
        unresolved: bool = False,
    ) -> dict[str, Any]:
        return self.write_policy.decide(
            object_type=object_type,
            load_bearing=load_bearing,
            verified=verified,
            unresolved=unresolved,
        ).to_dict()
