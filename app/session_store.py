"""
State-Memory Agent V1 — Session Store
Manages session folders and persistent session data:
- state_register.json (overwritten each turn)
- state_deltas.jsonl (append-only log)
- summary.json
"""

import json
import os
from pathlib import Path
from datetime import datetime

from .schemas import (
    BoundaryAwarenessResidue,
    BoundaryTraceEntry,
    ReadingPositionState,
    SessionSummary,
    StateDelta,
    StateRegister,
)


class SessionStore:
    def __init__(self, sessions_dir: str = "./sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._current_session_id: str = ""
        self._session_path: Path = Path(".")

    def start_session(self, session_id: str, objective: str = "") -> SessionSummary:
        """Create a new session folder and initial files."""
        self._current_session_id = session_id
        self._session_path = self.sessions_dir / session_id
        self._session_path.mkdir(parents=True, exist_ok=True)

        # Initialize state register
        initial_state = StateRegister(
            session_id=session_id,
            turn_id=0,
            coherence=0.80,
            drift=0.00,
            tool_overload=0.00,
            context_fragmentation=0.00,
        )
        self.save_state(initial_state)

        # Initialize empty delta log
        deltas_path = self._session_path / "state_deltas.jsonl"
        deltas_path.touch(exist_ok=True)

        # Initialize boundary-awareness persistence files
        boundary_trace_path = self._session_path / "boundary_trace.jsonl"
        boundary_trace_path.touch(exist_ok=True)

        self._save_json(
            self._session_path / "boundary_residue.json",
            {"status": "none"},
        )
        self.save_reading_position(ReadingPositionState.to_initial())

        # Initialize summary
        summary = SessionSummary(
            session_id=session_id,
            objective=objective,
        )
        self._save_json(self._session_path / "summary.json", summary.model_dump(mode="json"))

        return summary

    def save_state(self, state: StateRegister) -> None:
        """Overwrite current state register."""
        path = self._session_path / "state_register.json"
        self._save_json(path, state.model_dump(mode="json"))

    def load_state(self) -> StateRegister:
        """Load current state register."""
        path = self._session_path / "state_register.json"
        data = self._load_json(path)
        return StateRegister(**data)

    def append_delta(self, delta: StateDelta) -> None:
        """Append a delta entry to the log."""
        path = self._session_path / "state_deltas.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(delta.model_dump(mode="json")) + "\n")

    def load_recent_deltas(self, n: int = 10) -> list[StateDelta]:
        """Load the last N delta entries."""
        path = self._session_path / "state_deltas.jsonl"
        if not path.exists():
            return []

        lines = path.read_text(encoding="utf-8").strip().split("\n")
        lines = [l for l in lines if l.strip()]
        recent = lines[-n:]
        return [StateDelta(**json.loads(line)) for line in recent]

    def load_summary(self) -> SessionSummary:
        """Load current session summary."""
        path = self._session_path / "summary.json"
        data = self._load_json(path)
        return SessionSummary(**data)

    def update_summary_turn_count(self, turn_id: int) -> None:
        """Update the turn count in the session summary."""
        summary = self.load_summary()
        summary.turn_count = turn_id
        summary.updated_at = datetime.utcnow()
        self._save_json(
            self._session_path / "summary.json",
            summary.model_dump(mode="json"),
        )


    def append_boundary_trace(self, trace_entry: BoundaryTraceEntry) -> None:
        """Append one compact boundary-awareness trace row."""
        path = self._session_path / "boundary_trace.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace_entry.model_dump(mode="json")) + "\n")

    def save_boundary_residue(self, residue: BoundaryAwarenessResidue | dict) -> None:
        """Overwrite latest boundary-awareness residue persistence payload."""
        path = self._session_path / "boundary_residue.json"
        payload = residue.model_dump(mode="json") if isinstance(residue, BoundaryAwarenessResidue) else residue
        self._save_json(path, payload)

    def load_boundary_residue(self) -> dict:
        """Load latest compact boundary-awareness residue or status marker."""
        path = self._session_path / "boundary_residue.json"
        if not path.exists():
            return {"status": "none"}
        return self._load_json(path)

    def save_reading_position(self, reading_position: ReadingPositionState) -> None:
        """Overwrite current persisted reading_position runtime state."""
        path = self._session_path / "reading_position.json"
        self._save_json(path, reading_position.model_dump(mode="json"))

    def load_reading_position(self) -> ReadingPositionState:
        """Load current reading_position runtime state."""
        path = self._session_path / "reading_position.json"
        if not path.exists():
            initial = ReadingPositionState.to_initial()
            self.save_reading_position(initial)
            return initial
        return ReadingPositionState(**self._load_json(path))

    def _save_json(self, path: Path, data: dict) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def _load_json(self, path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
