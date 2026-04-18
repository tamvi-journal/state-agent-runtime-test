from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any

from deploy.logging_bootstrap import bootstrap_logging
from deploy.runtime_config import RuntimeConfig


@dataclass(slots=True)
class ProcessRunPlan:
    app_mode: str
    host: str
    port: int
    log_level: str
    app_module: str
    reload: bool
    server_command: list[str]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ProcessRunner:
    """
    Build a deployment/run plan without actually launching a server.

    This keeps process/deployment wiring inspectable and testable.
    """

    config: RuntimeConfig = field(default_factory=RuntimeConfig.from_env)

    def build_run_plan(self) -> ProcessRunPlan:
        logging_result = bootstrap_logging(log_level=self.config.log_level)

        cmd = [
            "uvicorn",
            self.config.app_module,
            "--host", self.config.host,
            "--port", str(self.config.port),
            "--log-level", logging_result.log_level,
        ]
        if self.config.reload:
            cmd.append("--reload")

        notes = [
            f"mode={self.config.app_mode}",
            f"webhook_base_path={self.config.webhook_base_path}",
            "this is a dry run plan, not a live server launch",
        ]

        return ProcessRunPlan(
            app_mode=self.config.app_mode,
            host=self.config.host,
            port=self.config.port,
            log_level=logging_result.log_level,
            app_module=self.config.app_module,
            reload=self.config.reload,
            server_command=cmd,
            notes=notes,
        )
