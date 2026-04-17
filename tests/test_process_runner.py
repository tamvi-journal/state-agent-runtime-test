from __future__ import annotations

from deploy.deployment_manifest import build_manifest
from deploy.logging_bootstrap import bootstrap_logging
from deploy.process_runner import ProcessRunner
from deploy.runtime_config import RuntimeConfig


def test_runtime_config_accepts_explicit_values() -> None:
    cfg = RuntimeConfig(
        app_mode="dev",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        app_module="server.app_factory:app",
        reload=True,
        webhook_base_path="/webhooks",
    )

    assert cfg.app_mode == "dev"
    assert cfg.port == 8000
    assert cfg.reload is True


def test_logging_bootstrap_normalizes_invalid_level() -> None:
    result = bootstrap_logging(log_level="LOUD")

    assert result.configured is True
    assert result.log_level == "info"


def test_process_runner_builds_uvicorn_style_run_plan() -> None:
    runner = ProcessRunner(
        config=RuntimeConfig(
            app_mode="dev",
            host="127.0.0.1",
            port=8000,
            log_level="debug",
            app_module="server.app_factory:app",
            reload=True,
            webhook_base_path="/webhooks",
        )
    )
    plan = runner.build_run_plan()

    assert plan.server_command[0] == "uvicorn"
    assert "server.app_factory:app" in plan.server_command
    assert "--reload" in plan.server_command
    assert "mode=dev" in plan.notes


def test_deployment_manifest_contains_startup_checks() -> None:
    cfg = RuntimeConfig(
        app_mode="prod",
        host="0.0.0.0",
        port=9000,
        log_level="warning",
        app_module="server.app_factory:app",
        reload=False,
        webhook_base_path="/webhooks",
    )
    manifest = build_manifest(config=cfg)

    assert manifest.app_mode == "prod"
    assert "APP_MODE" in manifest.recommended_env
    assert "config loaded" in manifest.startup_checks
