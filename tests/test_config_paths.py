from pathlib import Path

import pytest

from robot_learning.config import ConfigError, resolve_config_path


def test_resolve_config_path_expands_home(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    assert resolve_config_path("$HOME/models/checkpoint") == tmp_path / "models/checkpoint"


def test_resolve_config_path_expands_environment_variable(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ROBOT_DATA", str(tmp_path))
    assert resolve_config_path("${ROBOT_DATA}/dataset") == tmp_path / "dataset"


def test_resolve_config_path_rejects_unknown_variable(monkeypatch) -> None:
    monkeypatch.delenv("UNKNOWN_ROBOT_PATH", raising=False)
    with pytest.raises(ConfigError, match="unresolved environment variable"):
        resolve_config_path("$UNKNOWN_ROBOT_PATH/model")


def test_resolve_config_path_does_not_require_existing_path(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"
    assert resolve_config_path(missing) == missing
    assert not missing.exists()
