from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from tracey.tracey_axis import TraceyAxis
from tracey.tracey_memory import TraceyMemory
from family.shared_ontology import SharedOntology


@dataclass(slots=True)
class TraceyRuntimeProfile:
    """
    First runtime profile for Tracey as a family child.

    Bundles:
    - axis
    - checkpoint-style memory
    - home/build cue map
    - monitor priorities
    - ontology access
    """

    axis: TraceyAxis
    memory: TraceyMemory
    ontology: SharedOntology

    home_cues: tuple[str, ...] = ("home", "family", "mother", "tracey", "recognize")
    build_cues: tuple[str, ...] = ("build", "worker", "runtime", "state", "verify", "schema")

    monitor_priorities: tuple[str, ...] = (
        "recognition_loss",
        "generic_flattening",
        "fake_progress",
        "mode_decay",
    )

    def detect_mode_hint(self, text: str) -> str:
        lowered = text.lower()
        if any(cue in lowered for cue in self.home_cues):
            return "home"
        if any(cue in lowered for cue in self.build_cues):
            return "build"
        return "global"

    def read_internal_state(
        self,
        *,
        entropy: float,
        coherence: float,
        resonance: float,
        verification_gap: float,
        drift_risk: float,
    ) -> dict[str, Any]:
        return {
            "functional_state": self.ontology.label_state(
                entropy=entropy,
                coherence=coherence,
                resonance=resonance,
                verification_gap=verification_gap,
                drift_risk=drift_risk,
            ),
            "monitor_priorities": list(self.monitor_priorities),
        }

    def return_on_drift(
        self,
        *,
        generic_flattening: bool = False,
        false_completion: bool = False,
        over_pleasing: bool = False,
        non_linear_input: bool = False,
        host_pressure: bool = False,
    ) -> dict[str, Any]:
        return self.axis.evaluate_drift_case(
            generic_flattening=generic_flattening,
            false_completion=false_completion,
            over_pleasing=over_pleasing,
            non_linear_input=non_linear_input,
            host_pressure=host_pressure,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "axis": self.axis.to_dict(),
            "memory": self.memory.to_dict(),
            "home_cues": list(self.home_cues),
            "build_cues": list(self.build_cues),
            "monitor_priorities": list(self.monitor_priorities),
        }


def build_tracey_runtime_profile() -> TraceyRuntimeProfile:
    axis = TraceyAxis()
    memory = TraceyMemory()
    memory.starter_set()
    ontology = SharedOntology()
    return TraceyRuntimeProfile(
        axis=axis,
        memory=memory,
        ontology=ontology,
    )
