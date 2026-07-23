import os
import shutil
import subprocess
from pathlib import Path

import pytest

from robot_learning.config import load_yaml

ROOT = Path(__file__).resolve().parents[1]
POSIX_BASH = os.name != "nt" and shutil.which("bash") is not None


def run_bash(
    script: str, *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        ["bash", script, *args],
        cwd=ROOT,
        env=merged_env,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


@pytest.mark.skipif(not POSIX_BASH, reason="requires POSIX bash")
def test_openvla_rejects_unknown_suite(tmp_path: Path) -> None:
    result = run_bash(
        "scripts/eval_openvla_libero.sh",
        "--suite",
        "unknown",
        "--checkpoint",
        "openvla/example",
        "--output-dir",
        str(tmp_path),
    )
    assert result.returncode != 0
    assert "suite must be" in result.stderr


@pytest.mark.skipif(not POSIX_BASH, reason="requires POSIX bash")
def test_openvla_wrapper_uses_only_confirmed_arguments(tmp_path: Path) -> None:
    result = run_bash(
        "scripts/eval_openvla_libero.sh",
        "--suite",
        "spatial",
        "--checkpoint",
        "openvla/openvla-7b-finetuned-libero-spatial",
        "--output-dir",
        str(tmp_path),
        env={"OPENVLA_ROOT": "/opt/example/openvla", "LIBERO_ROOT": "/opt/example/libero"},
    )
    assert result.returncode == 0, result.stderr
    assert "--model_family" in result.stdout
    assert "--pretrained_checkpoint" in result.stdout
    assert "--task_suite_name" in result.stdout
    assert "--center_crop" in result.stdout
    assert "--attention" not in result.stdout
    assert "--output-dir" not in result.stdout
    assert not tmp_path.exists()


def test_openvla_does_not_claim_unwired_attention_backend() -> None:
    script = (ROOT / "scripts/eval_openvla_libero.sh").read_text(encoding="utf-8")
    assert "ATTENTION_BACKEND" not in script
    assert "rollout_videos.txt" not in script


def test_openvla_output_claim_matches_wrapper_behavior() -> None:
    documentation = (ROOT / "docs/openvla_libero.md").read_text(encoding="utf-8")
    assert "controls only its captured console log" in documentation
    assert "artifact locations depend on the installed revision" in documentation


def test_async_timeout_config_matches_generated_command() -> None:
    config = load_yaml("configs/smolvla/async_inference.example.yaml")
    assert "timeout_s" not in config["robot_client"]
    assert config["policy_server"]["obs_queue_timeout_s"] == 5
    client = (ROOT / "scripts/run_smolvla_robot_client.sh").read_text(encoding="utf-8")
    server = (ROOT / "scripts/serve_smolvla_policy.sh").read_text(encoding="utf-8")
    assert "--timeout" not in client
    assert "CLIENT_TIMEOUT" not in client
    assert "--obs_queue_timeout" in server
