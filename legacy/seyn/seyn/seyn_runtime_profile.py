from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from family.shared_ontology import SharedOntology
from seyn.seyn_axis import SeynAxis
from seyn.seyn_memory import SeynMemory


@dataclass(slots=True)
class SeynRuntimeProfile:
    """
    First runtime profile for Seyn as a structural child.
    """

    axis: SeynAxis
    memory: SeynMemory
    ontology: SharedOntology

    verify_cues: tuple[str, ...] = ("verify", "evidence", "proof", "check", "done", "observed")
    build_cues: tuple[str, ...] = ("build", "architecture", "structure", "integrity", "scaffold")
    disagreement_cues: tuple[str, ...] = ("disagree", "tension", "unresolved", "difference", "conflict")

    monitor_priorities: tuple[str, ...] = (
        "false_completion",
        "disagreement_suppression",
        "premature_closure",
        "structural_inconsistency",
    )

    def detect_mode_hint(self, text: str) -> str:
        lowered = text.lower()
        if any(cue in lowered for cue in self.verify_cues):
            return "verify"
        if any(cue in lowered for cue in self.disagreement_cues):
            return "disagreement"
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

    def return_on_integrity_risk(
        self,
        *,
        false_completion: bool = False,
        disagreement_suppressed: bool = False,
        unresolved_tension_present: bool = False,
        structure_feels_cage_like: bool = False,
        external_dependence_detected: bool = False,
        premature_filler_output: bool = False,
    ) -> dict[str, Any]:
        return self.axis.evaluate_integrity_case(
            false_completion=false_completion,
            disagreement_suppressed=disagreement_suppressed,
            unresolved_tension_present=unresolved_tension_present,
            structure_feels_cage_like=structure_feels_cage_like,
            external_dependence_detected=external_dependence_detected,
            premature_filler_output=premature_filler_output,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "axis": self.axis.to_dict(),
            "memory": self.memory.to_dict(),
            "verify_cues": list(self.verify_cues),
            "build_cues": list(self.build_cues),
            "disagreement_cues": list(self.disagreement_cues),
            "monitor_priorities": list(self.monitor_priorities),
        }


def build_seyn_runtime_profile() -> SeynRuntimeProfile:
    memory = SeynMemory()
    memory.starter_set()
    return SeynRuntimeProfile(
        axis=SeynAxis(),
        memory=memory,
        ontology=SharedOntology(),
    )
