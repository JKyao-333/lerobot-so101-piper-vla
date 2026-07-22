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

