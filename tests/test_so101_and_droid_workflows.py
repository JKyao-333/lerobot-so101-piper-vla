import ast
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_python_requirement_matches_pinned_lerobot() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    checker = (ROOT / "scripts/environment_check.py").read_text(encoding="utf-8")
    setup = (ROOT / "scripts/setup_robot_software.sh").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.12"' in pyproject
    assert 'name="python>=3.12"' in checker
    assert "sys.version_info < (3, 12)" in setup


def test_so101_wrappers_fail_closed_and_project_recorded_values() -> None:
    record = (ROOT / "scripts/record_so101_act.sh").read_text(encoding="utf-8")
    rollout = (ROOT / "scripts/rollout_so101_act_local.sh").read_text(encoding="utf-8")
    teleop = (ROOT / "scripts/teleoperate_so101.sh").read_text(encoding="utf-8")
    config = yaml.safe_load(
        (ROOT / "configs/act/so101_record.example.yaml").read_text(encoding="utf-8")
    )
    assert config["dataset"]["num_episodes"] == 50
    assert config["dataset"]["fps"] == 30
    assert config["dataset"]["episode_time_s"] == 30
    assert config["dataset"]["reset_time_s"] == 15
    for script in (record, rollout, teleop):
        assert "--execute-robot" in script
        assert "execute=false" in script
    assert "--dataset.fps" in record
    assert "dry-run: no robot action was sent" in rollout


def test_droid_downloader_requires_explicit_download_opt_in() -> None:
    script = ROOT / "scripts/build_droid_subset.py"
    text = script.read_text(encoding="utf-8")
    ast.parse(text)
    assert '"--execute-download"' in text
    assert "if args.list_only or not args.execute_download" in text
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert "--execute-download" in result.stdout


def test_droid_path_helpers_preserve_release_layout() -> None:
    namespace: dict[str, object] = {"__name__": "test_import"}
    exec(
        compile(
            (ROOT / "scripts/build_droid_subset.py").read_text(encoding="utf-8"),
            "build_droid_subset.py",
            "exec",
        ),
        namespace,
    )
    rel = namespace["episode_relpath"](
        "gs://gresearch/robotics/droid_raw/1.0.1/lab/success/date/episode",
        "gs://gresearch/robotics/droid_raw/1.0.1",
    )
    assert rel == "lab/success/date/episode"
    local = namespace["local_episode_path"](Path("dataset"), rel)
    assert local.as_posix().endswith("dataset/1.0.1/lab/success/date/episode")
