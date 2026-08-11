from pathlib import Path

import pytest

from robot_learning.config import ConfigError, load_yaml, validate_dual_act_config


def test_dual_act_example_is_valid() -> None:
    config = load_yaml(Path("configs/dual_act/dual_act.example.yaml"))
    validate_dual_act_config(config)


def test_missing_required_field_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("execute_robot: false\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="missing required field"):
        validate_dual_act_config(load_yaml(path))


def test_action_vectors_must_match_dimension() -> None:
    config = load_yaml("configs/dual_act/dual_act.example.yaml")
    config["safety"]["lower_bounds"] = [0]
    with pytest.raises(ConfigError, match="must contain"):
        validate_dual_act_config(config)


def test_public_profile_disallows_robot_execution() -> None:
    config = load_yaml("configs/dual_act/dual_act.example.yaml")
    assert config["allow_robot_execution"] is False


def test_front_and_wrist_camera_ids_must_differ() -> None:
    config = load_yaml("configs/dual_act/dual_act.example.yaml")
    config["wrist_camera"] = config["front_camera"]
    with pytest.raises(ConfigError, match="camera"):
        validate_dual_act_config(config)


def test_skill_checkpoints_must_be_distinct() -> None:
    config = load_yaml("configs/dual_act/dual_act.example.yaml")
    config["skills"]["b"]["checkpoint"] = config["skills"]["a"]["checkpoint"]
    with pytest.raises(ConfigError, match="checkpoints must be distinct"):
        validate_dual_act_config(config)


def test_invalid_safety_bounds_are_rejected() -> None:
    config = load_yaml("configs/dual_act/dual_act.example.yaml")
    config["safety"]["lower_bounds"][0] = config["safety"]["upper_bounds"][0]
    with pytest.raises(ConfigError, match="bounds must increase"):
        validate_dual_act_config(config)


def test_non_positive_step_delta_is_rejected() -> None:
    config = load_yaml("configs/dual_act/dual_act.example.yaml")
    config["safety"]["max_step_delta"][0] = 0
    with pytest.raises(ConfigError, match="must be positive"):
        validate_dual_act_config(config)
