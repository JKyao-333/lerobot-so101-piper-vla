import subprocess
import sys


def test_mock_cli_can_complete_non_interactively() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_dual_act.py",
            "--config",
            "configs/dual_act/dual_act.example.yaml",
            "--auto-confirm-mock",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "final stage: DONE" in result.stdout


def test_mock_auto_confirmation_is_forbidden_with_hardware() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_dual_act.py",
            "--hardware",
            "--auto-confirm-mock",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert "forbidden with --hardware" in result.stderr
