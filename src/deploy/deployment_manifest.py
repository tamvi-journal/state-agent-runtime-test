from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from deploy.runtime_config import RuntimeConfig


@dataclass(slots=True)
class DeploymentManifest:
    app_mode: str
    host: str
    port: int
    app_module: str
    reload: bool
    webhook_base_path: str
    recommended_env: list[str]
    startup_checks: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_manifest(*, config: RuntimeConfig) -> DeploymentManifest:
    return DeploymentManifest(
        app_mode=config.app_mode,
        host=config.host,
        port=config.port,
        app_module=config.app_module,
        reload=config.reload,
        webhook_base_path=config.webhook_base_path,
        recommended_env=[
            "APP_MODE",
            "APP_HOST",
            "APP_PORT",
            "LOG_LEVEL",
            "APP_MODULE",
            "APP_RELOAD",
            "WEBHOOK_BASE_PATH",
        ],
        startup_checks=[
            "config loaded",
            "logging bootstrap ready",
            "app factory import path set",
            "webhook base path defined",
        ],
    )
