"""Small, strict configuration helpers used by hardware-free validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised when a public configuration template is incomplete or malformed."""


def load_yaml(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.is_file():
        raise ConfigError(f"configuration file does not exist: {config_path}")
    try:
        value = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {config_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConfigError(f"top-level YAML value must be a mapping: {config_path}")
    return value


def require_path(config: dict[str, Any], dotted_path: str) -> Any:
    value: Any = config
    for part in dotted_path.split("."):
        if not isinstance(value, dict) or part not in value:
            raise ConfigError(f"missing required field: {dotted_path}")
        value = value[part]
    if value is None or value == "":
        raise ConfigError(f"required field is empty: {dotted_path}")
    return value


def validate_dual_act_config(config: dict[str, Any]) -> None:
    required = (
        "execute_robot",
        "control_hz",
        "total_timeout_s",
        "handoff_timeout_s",
        "skills.a.checkpoint",
        "skills.a.task",
        "skills.a.completion_s",
        "skills.a.timeout_s",
        "skills.b.checkpoint",
        "skills.b.task",
        "skills.b.completion_s",
        "skills.b.timeout_s",
        "safety.action_dim",
        "safety.lower_bounds",
        "safety.upper_bounds",
        "safety.max_step_delta",
    )
    for key in required:
        require_path(config, key)

    action_dim = int(require_path(config, "safety.action_dim"))
    for key in ("lower_bounds", "upper_bounds", "max_step_delta"):
        values = require_path(config, f"safety.{key}")
        if not isinstance(values, list) or len(values) != action_dim:
            raise ConfigError(f"safety.{key} must contain {action_dim} values")

    if float(require_path(config, "control_hz")) <= 0:
        raise ConfigError("control_hz must be positive")
    for key in ("total_timeout_s", "handoff_timeout_s"):
        if float(require_path(config, key)) <= 0:
            raise ConfigError(f"{key} must be positive")
    for skill in ("a", "b"):
        completion = float(require_path(config, f"skills.{skill}.completion_s"))
        timeout = float(require_path(config, f"skills.{skill}.timeout_s"))
        if completion <= 0 or timeout <= completion:
            raise ConfigError(f"skills.{skill}.timeout_s must be greater than completion_s")
