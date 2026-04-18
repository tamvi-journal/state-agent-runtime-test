from __future__ import annotations

from dataclasses import dataclass, asdict
import os
from pathlib import Path
from typing import Any

from memory_runtime.tier_types import DEFAULT_MEMORY_TIER_CONFIG, MemoryTierConfig

_ALLOWED_APP_MODES = {"dev", "prod", "test"}


@dataclass(slots=True)
class RuntimeConfig:
    app_mode: str
    host: str
    port: int
    log_level: str
    app_module: str
    reload: bool
    webhook_base_path: str

    def __post_init__(self) -> None:
        if self.app_mode not in _ALLOWED_APP_MODES:
            raise ValueError(f"invalid app_mode: {self.app_mode}")
        if not self.host.strip():
            raise ValueError("host must be non-empty")
        if not isinstance(self.port, int) or self.port <= 0:
            raise ValueError("port must be a positive int")
        if not self.app_module.strip():
            raise ValueError("app_module must be non-empty")
        if not self.webhook_base_path.startswith("/"):
            raise ValueError("webhook_base_path must start with '/'")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        app_mode = os.getenv("APP_MODE", "dev").strip().lower()
        host = os.getenv("APP_HOST", "127.0.0.1").strip()
        port = int(os.getenv("APP_PORT", "8000"))
        log_level = os.getenv("LOG_LEVEL", "info").strip().lower()
        app_module = os.getenv("APP_MODULE", "server.app_factory:app").strip()
        reload = os.getenv("APP_RELOAD", "true" if app_mode == "dev" else "false").strip().lower() in {"1", "true", "yes"}
        webhook_base_path = os.getenv("WEBHOOK_BASE_PATH", "/webhooks").strip()

        return cls(
            app_mode=app_mode,
            host=host,
            port=port,
            log_level=log_level,
            app_module=app_module,
            reload=reload,
            webhook_base_path=webhook_base_path,
        )


def load_memory_tier_config(*, config_path: str | None = None) -> MemoryTierConfig:
    resolved_path = _resolve_repo_config_path(config_path)
    if resolved_path is None or not resolved_path.exists():
        return DEFAULT_MEMORY_TIER_CONFIG

    section_values = _read_top_level_yaml_section(resolved_path, "memory_tiers")
    if not section_values:
        return DEFAULT_MEMORY_TIER_CONFIG

    merged = asdict(DEFAULT_MEMORY_TIER_CONFIG)
    for field_name, current_value in merged.items():
        if field_name not in section_values:
            continue
        merged[field_name] = _coerce_config_value(section_values[field_name], current_value)
    return MemoryTierConfig(**merged)


def _resolve_repo_config_path(config_path: str | None) -> Path | None:
    explicit = (config_path or os.getenv("STATE_MEMORY_CONFIG_PATH", "")).strip()
    if explicit:
        return Path(explicit)

    repo_root = Path(__file__).resolve().parents[2]
    root_config = repo_root / "config.yaml"
    if root_config.exists():
        return root_config

    nested_config = repo_root / "config" / "config.yaml"
    if nested_config.exists():
        return nested_config
    return None


def _read_top_level_yaml_section(path: Path, section_name: str) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    in_section = False
    values: dict[str, str] = {}

    for raw_line in lines:
        line_without_comment = raw_line.split("#", 1)[0].rstrip()
        if not line_without_comment.strip():
            continue

        indent = len(line_without_comment) - len(line_without_comment.lstrip(" "))
        stripped = line_without_comment.strip()

        if not in_section:
            if indent == 0 and stripped == f"{section_name}:":
                in_section = True
            continue

        if indent == 0:
            break

        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        values[key.strip()] = value.strip()

    return values


def _coerce_config_value(raw_value: str, current_value: Any) -> Any:
    normalized = raw_value.strip().strip("'").strip('"')

    if isinstance(current_value, bool):
        return normalized.lower() in {"1", "true", "yes", "on"}

    if isinstance(current_value, int):
        return int(normalized)

    return normalized
