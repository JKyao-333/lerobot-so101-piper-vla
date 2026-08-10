import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/environment_check.py"


def run_environment_check(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_environment_check_reports_presence_without_hardware_claims() -> None:
    result = run_environment_check("--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["tool"] == "environment_check"
    assert report["profile"] == "deployment"
    assert report["read_only"] is True
    assert report["overall_status"] in {"PASS", "INCOMPLETE"}
    assert report["deployment_evidence_status"] == "NOT_VERIFIED"
    assert {item["category"] for item in report["checks"]} >= {
        "python",
        "package",
        "config",
        "checkpoint",
        "camera",
        "can",
    }


def test_software_profile_excludes_hardware_presence_checks() -> None:
    result = run_environment_check("--profile", "software", "--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["profile"] == "software"
    assert {item["category"] for item in report["checks"]} == {
        "python",
        "package",
        "config",
    }


def test_strict_mode_fails_when_deployment_items_are_missing(tmp_path: Path) -> None:
    existing_checkpoint = tmp_path / "checkpoint_a"
    existing_checkpoint.mkdir()
    (existing_checkpoint / "placeholder").write_text("test", encoding="utf-8")
    private_marker = "private-checkpoint-marker"
    config = {
        "can_interface": "missing_can_for_test",
        "front_camera": 987,
        "wrist_camera": 988,
        "skills": {
            "a": {"checkpoint": str(existing_checkpoint)},
            "b": {"checkpoint": str(tmp_path / private_marker)},
        },
    }
    config_path = tmp_path / "deployment.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    result = run_environment_check("--config", str(config_path), "--json", "--strict")
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["overall_status"] == "INCOMPLETE"
    checkpoint_results = [
        item for item in report["checks"] if item["category"] == "checkpoint"
    ]
    assert {item["status"] for item in checkpoint_results} >= {"PRESENT", "MISSING"}
    assert private_marker not in result.stdout


def test_invalid_dual_act_semantics_fail_config_check(tmp_path: Path) -> None:
    config = yaml.safe_load(
        (ROOT / "configs/dual_act/dual_act.example.yaml").read_text(encoding="utf-8")
    )
    config["skills"]["a"]["timeout_s"] = config["skills"]["a"]["completion_s"]
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    result = run_environment_check(
        "--profile", "software", "--config", str(config_path), "--json", "--strict"
    )
    assert result.returncode == 1
    report = json.loads(result.stdout)
    config_result = next(item for item in report["checks"] if item["name"] == "deployment_config")
    assert config_result["status"] == "FAIL"


def test_environment_check_uses_no_execution_or_process_modules() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", maxsplit=1)[0])
    assert imported_roots.isdisjoint({"subprocess", "lerobot", "lerobot_robot_piper", "piper_sdk"})


def test_environment_check_does_not_write_to_inspected_directory(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("name: software-check\n", encoding="utf-8")
    before = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}
    result = run_environment_check(
        "--profile", "software", "--config", str(config_path), "--json"
    )
    after = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}
    assert result.returncode == 0
    assert after == before
