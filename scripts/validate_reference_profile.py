#!/usr/bin/env python3
"""Validate and summarize the trusted manual-reference profile without hardware."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from robot_learning.config import (
    ConfigError,
    load_yaml,
    require_path,
    resolve_config_path,
    validate_manual_reference_config,
)


def validate_projected_configs(config: dict[str, Any], root: Path = Path(".")) -> None:
    """Ensure workflow-facing examples stay aligned with the reference source of truth."""

    record = load_yaml(root / "configs/act/record.example.yaml")
    train = load_yaml(root / "configs/act/train.example.yaml")
    rollout = load_yaml(root / "configs/act/rollout.example.yaml")
    dual = load_yaml(root / "configs/dual_act/dual_act.example.yaml")
    openvla = load_yaml(root / "configs/openvla/libero_eval.example.yaml")
    finetune = load_yaml(root / "configs/smolvla/finetune.example.yaml")
    async_config = load_yaml(root / "configs/smolvla/async_inference.example.yaml")
    sync_config = load_yaml(root / "configs/smolvla/sync_rollout.example.yaml")

    checks = (
        (
            "ACT record task",
            require_path(record, "dataset.task"),
            config["scenario"]["single_task"],
        ),
        (
            "ACT record episodes",
            require_path(record, "dataset.num_episodes"),
            config["act"]["recording"]["num_episodes"],
        ),
        (
            "ACT training steps",
            require_path(train, "training.steps"),
            config["act"]["training"]["reference_checkpoint_step"],
        ),
        ("ACT rollout task", require_path(rollout, "task"), config["scenario"]["single_task"]),
        (
            "dual ACT control rate",
            require_path(dual, "control_hz"),
            config["dual_act"]["control_hz"],
        ),
        (
            "dual ACT execution permission",
            require_path(dual, "allow_robot_execution"),
            config["dual_act"]["allow_robot_execution"],
        ),
        ("dual ACT skill A", require_path(dual, "skills.a.task"), config["scenario"]["skill_a"]),
        ("dual ACT skill B", require_path(dual, "skills.b.task"), config["scenario"]["skill_b"]),
        (
            "OpenVLA suite map",
            require_path(openvla, "suites"),
            config["openvla_libero"]["suites"],
        ),
        (
            "SmolVLA Piper steps",
            require_path(finetune, "max_steps"),
            config["smolvla_piper"]["steps"],
        ),
        (
            "SmolVLA async actions per chunk",
            require_path(async_config, "robot_client.actions_per_chunk"),
            config["smolvla_async"]["actions_per_chunk"],
        ),
    )
    mismatches = [name for name, actual, expected in checks if actual != expected]
    if mismatches:
        raise ConfigError("reference projections are out of sync: " + ", ".join(mismatches))

    path_values = (
        require_path(record, "dataset.root"),
        require_path(train, "dataset.root"),
        require_path(train, "training.output_dir"),
        require_path(rollout, "checkpoint"),
        require_path(finetune, "dataset_root"),
        require_path(finetune, "output_dir"),
        require_path(sync_config, "log_file"),
    )
    for value in path_values:
        resolve_config_path(value)


def build_summary(config: dict[str, Any]) -> dict[str, Any]:
    actions = int(require_path(config, "smolvla_async.actions_per_chunk"))
    control_fps = int(require_path(config, "smolvla_async.control_fps"))
    suites = require_path(config, "openvla_libero.suites")
    return {
        "status": "valid",
        "profile_kind": require_path(config, "provenance.kind"),
        "hardware_measured": require_path(config, "provenance.hardware_measured"),
        "task": require_path(config, "scenario.single_task"),
        "recording_episodes": int(require_path(config, "act.recording.num_episodes")),
        "dataset_fps": int(require_path(config, "act.recording.dataset_fps")),
        "act_reference_checkpoint_step": int(
            require_path(config, "act.training.reference_checkpoint_step")
        ),
        "smolvla_piper_steps": int(require_path(config, "smolvla_piper.steps")),
        "smolvla_chunk_duration_s": round(actions / control_fps, 3),
        "openvla_suites": list(suites),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="configs/reference/manual_reference.yaml",
        type=Path,
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_yaml(args.config)
    validate_manual_reference_config(config)
    validate_projected_configs(config)
    summary = build_summary(config)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("manual reference profile: valid")
        print("hardware measurement claimed: no")
        print(f"task: {summary['task']}")
        print(
            "recording: "
            f"{summary['recording_episodes']} episodes at {summary['dataset_fps']} FPS"
        )
        print(f"ACT reference checkpoint: {summary['act_reference_checkpoint_step']} steps")
        print(f"SmolVLA Piper training: {summary['smolvla_piper_steps']} steps")
        print(f"SmolVLA chunk coverage: {summary['smolvla_chunk_duration_s']:.3f} s")
        print(f"OpenVLA suites: {', '.join(summary['openvla_suites'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
