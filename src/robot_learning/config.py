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


def validate_manual_reference_config(config: dict[str, Any]) -> None:
    """Validate the trusted, hardware-free reference profile derived from the manuals."""

    required = (
        "provenance.kind",
        "provenance.hardware_measured",
        "provenance.sources",
        "scenario.single_task",
        "scenario.long_horizon_task",
        "scenario.skill_a",
        "scenario.skill_b",
        "hardware.can_interface",
        "hardware.can_bitrate",
        "hardware.leader_port",
        "hardware.cameras.front.index_or_path",
        "hardware.cameras.wrist.index_or_path",
        "act.recording.dataset_repo_id",
        "act.recording.num_episodes",
        "act.recording.dataset_fps",
        "act.training.reference_checkpoint_step",
        "act.rollout.duration_s",
        "dual_act.control_hz",
        "dual_act.total_timeout_s",
        "dual_act.handoff_timeout_s",
        "dual_act.action_dim",
        "dual_act.joint_bounds",
        "dual_act.gripper_bounds",
        "openvla_libero.suites",
        "smolvla_piper.steps",
        "smolvla_piper.save_freq",
        "smolvla_async.control_fps",
        "smolvla_async.actions_per_chunk",
        "smolvla_async.nominal_chunk_duration_s",
        "smolvla_libero_optional.steps",
        "smolvla_libero_optional.save_freq",
        "smolvla_libero_optional.eval_episodes_per_task",
    )
    for key in required:
        require_path(config, key)

    if require_path(config, "provenance.kind") != "manual_example":
        raise ConfigError("provenance.kind must be manual_example")
    if require_path(config, "provenance.hardware_measured") is not False:
        raise ConfigError("manual reference profile must not claim hardware measurement")
    sources = require_path(config, "provenance.sources")
    if not isinstance(sources, list) or len(sources) < 7:
        raise ConfigError("provenance.sources must list the manuals and supplemental code")

    positive_paths = (
        "hardware.can_bitrate",
        "act.recording.num_episodes",
        "act.recording.episode_time_s",
        "act.recording.reset_time_s",
        "act.recording.dataset_fps",
        "act.training.reference_checkpoint_step",
        "act.rollout.duration_s",
        "dual_act.control_hz",
        "dual_act.total_timeout_s",
        "dual_act.handoff_timeout_s",
        "smolvla_piper.steps",
        "smolvla_piper.save_freq",
        "smolvla_async.actions_per_chunk",
        "smolvla_libero_optional.steps",
        "smolvla_libero_optional.save_freq",
        "smolvla_libero_optional.eval_episodes_per_task",
    )
    for key in positive_paths:
        if float(require_path(config, key)) <= 0:
            raise ConfigError(f"{key} must be positive")

    for name in ("front", "wrist"):
        for field in ("width", "height", "fps"):
            if int(require_path(config, f"hardware.cameras.{name}.{field}")) <= 0:
                raise ConfigError(f"hardware.cameras.{name}.{field} must be positive")

    dataset_fps = float(require_path(config, "act.recording.dataset_fps"))
    if dataset_fps != float(require_path(config, "dual_act.control_hz")):
        raise ConfigError("dual ACT control rate must match the ACT dataset rate")
    if dataset_fps != float(require_path(config, "smolvla_async.control_fps")):
        raise ConfigError("SmolVLA async control rate must match the dataset rate")

    single_task = require_path(config, "scenario.single_task")
    if single_task != require_path(config, "scenario.skill_a"):
        raise ConfigError("scenario.skill_a must reuse the single-task instruction")
    if single_task not in require_path(config, "scenario.long_horizon_task"):
        raise ConfigError("long-horizon instruction must contain skill A")

    action_dim = int(require_path(config, "dual_act.action_dim"))
    if action_dim != 7:
        raise ConfigError("Piper reference action_dim must be 7")
    for name in ("joint_bounds", "gripper_bounds"):
        bounds = require_path(config, f"dual_act.{name}")
        if not isinstance(bounds, list) or len(bounds) != 2 or bounds[0] >= bounds[1]:
            raise ConfigError(f"dual_act.{name} must be an increasing two-value list")

    piper_steps = int(require_path(config, "smolvla_piper.steps"))
    piper_save = int(require_path(config, "smolvla_piper.save_freq"))
    libero_steps = int(require_path(config, "smolvla_libero_optional.steps"))
    libero_save = int(require_path(config, "smolvla_libero_optional.save_freq"))
    if piper_steps % piper_save or libero_steps % libero_save:
        raise ConfigError("training steps must be divisible by checkpoint save frequency")

    actions = float(require_path(config, "smolvla_async.actions_per_chunk"))
    nominal = float(require_path(config, "smolvla_async.nominal_chunk_duration_s"))
    if abs(actions / dataset_fps - nominal) > 1e-6:
        raise ConfigError("SmolVLA nominal chunk duration is inconsistent")

    suites = require_path(config, "openvla_libero.suites")
    if not isinstance(suites, dict) or set(suites) != {"spatial", "object", "goal", "long"}:
        raise ConfigError("OpenVLA suites must contain spatial, object, goal, and long")
