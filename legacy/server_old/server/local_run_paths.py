from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from deploy.process_runner import ProcessRunner
from deploy.runtime_config import RuntimeConfig


@dataclass(slots=True)
class LocalRunPath:
    description: str
    command: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_local_run_paths(config: RuntimeConfig) -> dict[str, Any]:
    runner = ProcessRunner(config=config)
    run_plan = runner.build_run_plan()

    return {
        "preferred": LocalRunPath(
            description="Run the real FastAPI app with uvicorn",
            command=run_plan.server_command,
        ).to_dict(),
        "manual": LocalRunPath(
            description="Run module-style if using python -m uvicorn",
            command=[
                "python",
                "-m",
                "uvicorn",
                config.app_module,
                "--host",
                config.host,
                "--port",
                str(config.port),
                "--log-level",
                config.log_level,
            ] + (["--reload"] if config.reload else []),
        ).to_dict(),
        "notes": run_plan.notes,
    }
