"""Small, strict configuration helpers used by hardware-free validation."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised when a public configuration template is incomplete or malformed."""


_ENV_PATTERN = re.compile(r"\$(?:\{[^}]+\}|[A-Za-z_][A-Za-z0-9_]*)")


def resolve_config_path(value: str | Path) -> Path:
    """Expand user and environment syntax without requiring the path to exist."""

    raw = str(value)
    home = os.environ.get("HOME") or str(Path.home())
    portable_raw = re.sub(r"\$(?:\{HOME\}|HOME(?![A-Za-z0-9_]))", lambda _: home, raw)
    expanded = os.path.expandvars(portable_raw)
    if _ENV_PATTERN.search(expanded):
        raise ConfigError(f"path contains an unresolved environment variable: {raw}")
    return Path(expanded).expanduser()


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
        "allow_robot_execution",
        "allow_shared_checkpoint",
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

    for key in ("allow_robot_execution", "allow_shared_checkpoint"):
        if not isinstance(require_path(config, key), bool):
            raise ConfigError(f"{key} must be a boolean")

    action_dim = int(require_path(config, "safety.action_dim"))
    for key in ("lower_bounds", "upper_bounds", "max_step_delta"):
        values = require_path(config, f"safety.{key}")
        if not isinstance(values, list) or len(values) != action_dim:
            raise ConfigError(f"safety.{key} must contain {action_dim} values")

    lower_bounds = require_path(config, "safety.lower_bounds")
    upper_bounds = require_path(config, "safety.upper_bounds")
    max_step_delta = require_path(config, "safety.max_step_delta")
    for index, (lower, upper, delta) in enumerate(
        zip(lower_bounds, upper_bounds, max_step_delta, strict=True)
    ):
        if float(lower) >= float(upper):
            raise ConfigError(f"safety bounds must increase at index {index}")
        if float(delta) <= 0:
            raise ConfigError(f"safety.max_step_delta must be positive at index {index}")

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

    task_a = str(require_path(config, "skills.a.task")).strip()
    task_b = str(require_path(config, "skills.b.task")).strip()
    if not task_a or not task_b or task_a == task_b:
        raise ConfigError("skill A and skill B tasks must be non-empty and distinct")

    checkpoint_a = str(require_path(config, "skills.a.checkpoint"))
    checkpoint_b = str(require_path(config, "skills.b.checkpoint"))
    if checkpoint_a == checkpoint_b and not require_path(config, "allow_shared_checkpoint"):
        raise ConfigError("skill checkpoints must be distinct unless allow_shared_checkpoint=true")

    if "front_camera" in config and "wrist_camera" in config:
        if config["front_camera"] == config["wrist_camera"]:
            raise ConfigError("front_camera and wrist_camera must be distinct")


def validate_experiment_baseline(config: dict[str, Any]) -> None:
    """Validate the user-confirmed experiment baseline and revision boundary."""

    required = (
        "provenance.kind",
        "provenance.user_confirmed",
        "provenance.source_experiment.hardware_operated",
        "provenance.source_experiment.robot_teleoperation_completed",
        "provenance.source_experiment.dataset_recording_completed",
        "provenance.source_experiment.training_completed",
        "provenance.source_experiment.evaluation_completed",
        "provenance.source_experiment.rollout_completed",
        "provenance.source_experiment.values_from_experiment_records",
        "provenance.repository_revision.offline_validated",
        "provenance.repository_revision.mock_validated",
        "provenance.repository_revision.ci_validated",
        "provenance.repository_revision.hardware_replayed_on_current_commit",
        "provenance.sources",
        "value_scope.hardware_identity_fields",
        "value_scope.experiment_parameters",
        "value_scope.paths",
        "value_scope.performance_metrics",
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
        "dual_act.allow_robot_execution",
        "dual_act.allow_shared_checkpoint",
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

    if require_path(config, "provenance.kind") != "measured_experiment_baseline":
        raise ConfigError("provenance.kind must be measured_experiment_baseline")
    true_provenance_fields = (
        "provenance.user_confirmed",
        "provenance.source_experiment.hardware_operated",
        "provenance.source_experiment.robot_teleoperation_completed",
        "provenance.source_experiment.dataset_recording_completed",
        "provenance.source_experiment.training_completed",
        "provenance.source_experiment.evaluation_completed",
        "provenance.source_experiment.rollout_completed",
        "provenance.source_experiment.values_from_experiment_records",
        "provenance.repository_revision.offline_validated",
        "provenance.repository_revision.mock_validated",
        "provenance.repository_revision.ci_validated",
    )
    for key in true_provenance_fields:
        if require_path(config, key) is not True:
            raise ConfigError(f"{key} must be true")
    replayed = require_path(
        config, "provenance.repository_revision.hardware_replayed_on_current_commit"
    )
    if replayed is not False:
        raise ConfigError(
            "provenance.repository_revision.hardware_replayed_on_current_commit must be false"
        )
    expected_scopes = {
        "value_scope.hardware_identity_fields": "host_specific",
        "value_scope.experiment_parameters": "experiment_recorded",
        "value_scope.paths": "environment_specific",
        "value_scope.performance_metrics": "publish_only_with_evidence",
    }
    for key, expected in expected_scopes.items():
        if require_path(config, key) != expected:
            raise ConfigError(f"{key} must be {expected}")
    if require_path(config, "dual_act.allow_robot_execution") is not False:
        raise ConfigError("public experiment baseline must disallow robot execution")
    if not isinstance(require_path(config, "dual_act.allow_shared_checkpoint"), bool):
        raise ConfigError("dual_act.allow_shared_checkpoint must be a boolean")
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
    if require_path(config, "hardware.cameras.front.index_or_path") == require_path(
        config, "hardware.cameras.wrist.index_or_path"
    ):
        raise ConfigError("front and wrist camera identifiers must be distinct")

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

    forbidden_claim_keys = {
        "invented_success_rate",
        "invented_latency",
        "invented_loss",
        "industrial_grade",
        "production_verified",
        "safety_certified",
    }

    metric_evidence_fields = {
        "evidence_path",
        "evaluation_date",
        "episodes_or_tasks",
        "source_record",
    }

    def validate_claims(value: Any, location: str = "root") -> set[str]:
        if isinstance(value, dict):
            found = forbidden_claim_keys.intersection(value)
            if "success_rate" in value:
                missing = sorted(metric_evidence_fields.difference(value))
                if missing:
                    raise ConfigError(
                        f"success_rate at {location} requires evidence metadata: "
                        + ", ".join(missing)
                    )
            for key, child in value.items():
                found.update(validate_claims(child, f"{location}.{key}"))
            return found
        if isinstance(value, list):
            found: set[str] = set()
            for index, child in enumerate(value):
                found.update(validate_claims(child, f"{location}[{index}]"))
            return found
        return set()

    forbidden = validate_claims(config)
    if forbidden:
        raise ConfigError(
            "experiment baseline contains unsupported claims: " + ", ".join(sorted(forbidden))
        )

    piper_paths = (
        str(require_path(config, "act.rollout.local_checkpoint")),
        str(require_path(config, "smolvla_piper.checkpoint")),
    )
    if any("openvla" in path.lower() for path in piper_paths):
        raise ConfigError("OpenVLA checkpoints cannot be used for Piper rollout")
    suite_checkpoints = {
        str(require_path(config, f"openvla_libero.suites.{suite}.checkpoint"))
        for suite in ("spatial", "object", "goal", "long")
    }
    if str(require_path(config, "smolvla_piper.checkpoint")) in suite_checkpoints:
        raise ConfigError("SmolVLA Piper checkpoint cannot be an OpenVLA LIBERO suite checkpoint")
