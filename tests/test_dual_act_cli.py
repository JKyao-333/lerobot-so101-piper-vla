import os
import subprocess
import sys
from pathlib import Path

import yaml

from robot_learning.config import load_yaml

ROOT = Path(__file__).resolve().parents[1]


def write_execution_enabled_config(path: Path) -> Path:
    config = load_yaml("configs/dual_act/dual_act.example.yaml")
    config["allow_robot_execution"] = True
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    source_path = str(ROOT / "src")
    env["PYTHONPATH"] = os.pathsep.join(
        value for value in (source_path, env.get("PYTHONPATH", "")) if value
    )
    return subprocess.run(
        [sys.executable, "scripts/run_dual_act.py", *args],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_mock_cli_can_complete_non_interactively() -> None:
    result = run_cli(
        "--config",
        "configs/dual_act/dual_act.example.yaml",
        "--auto-confirm-mock",
    )
    assert result.returncode == 0, result.stderr
    assert "final stage: DONE" in result.stdout


def test_mock_auto_confirmation_is_forbidden_with_hardware() -> None:
    result = run_cli("--hardware", "--auto-confirm-mock")
    assert result.returncode != 0
    assert "forbidden with --hardware" in result.stderr


def test_execute_robot_requires_hardware() -> None:
    result = run_cli("--execute-robot")
    assert result.returncode != 0
    assert "--execute-robot requires --hardware" in result.stderr


def test_execute_robot_rejected_when_config_disallows() -> None:
    result = run_cli(
        "--hardware",
        "--execute-robot",
        "--config",
        "configs/dual_act/dual_act.example.yaml",
    )
    assert result.returncode != 0
    assert "requires both allow_robot_execution=true" in result.stderr
    assert "hardware mode requires" not in result.stderr


def test_config_permission_alone_does_not_execute(tmp_path: Path) -> None:
    config_path = write_execution_enabled_config(tmp_path / "enabled.yaml")
    result = run_cli("--config", str(config_path), "--auto-confirm-mock")
    assert result.returncode == 0, result.stderr
    assert "final stage: DONE" in result.stdout


def test_mock_mode_never_executes_robot(tmp_path: Path) -> None:
    config_path = write_execution_enabled_config(tmp_path / "enabled.yaml")
    result = run_cli("--config", str(config_path), "--execute-robot")
    assert result.returncode != 0
    assert "--execute-robot requires --hardware" in result.stderr
