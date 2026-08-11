import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
POSIX_BASH = os.name != "nt" and shutil.which("bash") is not None
LEROBOT_COMMIT = "e40b58a8dfa9e7b86918c374791599d070518d11"
PIPER_ADAPTER_COMMIT = "abf721d9e88ac822b18cb3413a75bb8cc0e3b34f"


def test_runtime_requirements_use_evidence_backed_source_pins() -> None:
    requirements = (ROOT / "requirements/robot-runtime.txt").read_text(encoding="utf-8")
    requirements_pins = set(re.findall(r"@([0-9a-f]{40})$", requirements, flags=re.MULTILINE))
    expected = {LEROBOT_COMMIT, PIPER_ADAPTER_COMMIT}
    assert requirements_pins == expected
    for documentation in ("docs/upstream_versions.md", "requirements/README.md"):
        text = (ROOT / documentation).read_text(encoding="utf-8")
        documented_pins = set(
            re.findall(r"(?<![0-9a-f])([0-9a-f]{40})(?![0-9a-f])", text)
        )
        assert documented_pins == expected


def test_required_distribution_manifest_is_the_single_inventory() -> None:
    manifest = ROOT / "configs/software/required_distributions.txt"
    packages = {
        line.strip()
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    assert packages == {"PyYAML", "lerobot", "lerobot_robot_piper", "piper_sdk"}
    checker = (ROOT / "scripts/environment_check.py").read_text(encoding="utf-8")
    shell_checker = (ROOT / "scripts/check_robot_environment.sh").read_text(encoding="utf-8")
    assert "required_distributions.txt" in checker
    assert "required_distributions.txt" in shell_checker


@pytest.mark.skipif(not POSIX_BASH, reason="requires POSIX bash")
def test_software_setup_defaults_to_preview(tmp_path: Path) -> None:
    venv_dir = tmp_path / "preview-venv"
    env = os.environ.copy()
    env["VENV_DIR"] = str(venv_dir)
    result = subprocess.run(
        ["bash", "scripts/setup_robot_software.sh"],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "requirements/robot-runtime.txt" in result.stdout
    assert "no package was downloaded" in result.stdout
    assert not venv_dir.exists()
