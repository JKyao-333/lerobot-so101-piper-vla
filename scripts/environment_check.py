#!/usr/bin/env python3
"""Read-only prerequisite checks for the Piper robot-learning workflows."""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import stat
import sys
from dataclasses import dataclass
from enum import StrEnum
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_MANIFEST = REPO_ROOT / "configs/software/required_distributions.txt"
ENV_PATTERN = re.compile(r"\$(?:\{[^}]+\}|[A-Za-z_][A-Za-z0-9_]*)")
REQUIRED_ENV_KEYS = (
    "LEADER_PORT",
    "CAN_INTERFACE",
    "CAN_BITRATE",
    "FRONT_CAMERA",
    "WRIST_CAMERA",
    "TASK_TEXT",
    "DATASET_ROOT",
    "CHECKPOINT_PATH",
    "DEVICE",
)


class CheckStatus(StrEnum):
    PASS = "PASS"
    PRESENT = "PRESENT"
    MISSING = "MISSING"
    FAIL = "FAIL"
    NOT_CHECKED = "NOT_CHECKED"


ACCEPTED_STATUSES = {CheckStatus.PASS, CheckStatus.PRESENT}


@dataclass(frozen=True)
class CheckResult:
    category: str
    name: str
    status: CheckStatus
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {
            "category": self.category,
            "name": self.name,
            "status": self.status.value,
            "detail": self.detail,
        }


def check_python() -> CheckResult:
    supported = sys.version_info >= (3, 12)
    detected = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return CheckResult(
        category="python",
        name="python>=3.12",
        status=CheckStatus.PASS if supported else CheckStatus.FAIL,
        detail=f"detected {detected}",
    )


def load_package_manifest(path: Path) -> tuple[CheckResult, list[str]]:
    try:
        names = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    except OSError:
        return (
            CheckResult(
                "package",
                "required_distribution_manifest",
                CheckStatus.MISSING,
                "manifest is missing",
            ),
            [],
        )
    if not names:
        return (
            CheckResult(
                "package",
                "required_distribution_manifest",
                CheckStatus.FAIL,
                "manifest contains no distributions",
            ),
            [],
        )
    return (
        CheckResult(
            "package",
            "required_distribution_manifest",
            CheckStatus.PASS,
            "manifest loaded",
        ),
        names,
    )


def check_packages(package_names: list[str]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for package in package_names:
        try:
            installed_version = version(package)
        except PackageNotFoundError:
            results.append(
                CheckResult(
                    "package", package, CheckStatus.MISSING, "distribution is not installed"
                )
            )
        else:
            results.append(
                CheckResult("package", package, CheckStatus.PASS, f"version {installed_version}")
            )
    return results


def inspect_config(config_path: Path) -> tuple[CheckResult, dict[str, Any] | None]:
    if not config_path.is_file():
        return (
            CheckResult("config", "deployment_config", CheckStatus.MISSING, "file is missing"),
            None,
        )
    try:
        import yaml
    except ImportError:
        return (
            CheckResult(
                "config",
                "deployment_config",
                CheckStatus.FAIL,
                "file exists but PyYAML is unavailable",
            ),
            None,
        )
    try:
        parsed = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return (
            CheckResult("config", "deployment_config", CheckStatus.FAIL, "YAML parsing failed"),
            None,
        )
    if not isinstance(parsed, dict):
        return (
            CheckResult(
                "config",
                "deployment_config",
                CheckStatus.FAIL,
                "top level is not a mapping",
            ),
            None,
        )

    dual_act_markers = {"allow_robot_execution", "skills", "safety"}
    if dual_act_markers.issubset(parsed):
        src_path = str(REPO_ROOT / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        try:
            from robot_learning.config import validate_dual_act_config
        except ImportError:
            return (
                CheckResult(
                    "config",
                    "deployment_config",
                    CheckStatus.FAIL,
                    "dual ACT validator is unavailable",
                ),
                None,
            )
        try:
            validate_dual_act_config(parsed)
        except (TypeError, ValueError):
            return (
                CheckResult(
                    "config",
                    "deployment_config",
                    CheckStatus.FAIL,
                    "dual ACT semantic validation failed",
                ),
                None,
            )
    return (
        CheckResult(
            "config",
            "deployment_config",
            CheckStatus.PASS,
            "file exists and configured semantics passed",
        ),
        parsed,
    )


def inspect_env_file(path: Path) -> tuple[CheckResult, dict[str, str] | None]:
    if not path.is_file():
        return (
            CheckResult("config", "host_env_file", CheckStatus.MISSING, "local .env is missing"),
            None,
        )
    values: dict[str, str] = {}
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", maxsplit=1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    except OSError:
        return (
            CheckResult("config", "host_env_file", CheckStatus.FAIL, "local .env is unreadable"),
            None,
        )
    missing = [key for key in REQUIRED_ENV_KEYS if not values.get(key)]
    if missing:
        return (
            CheckResult(
                "config",
                "host_env_file",
                CheckStatus.FAIL,
                "required variables are missing: " + ", ".join(missing),
            ),
            values,
        )
    return (
        CheckResult(
            "config",
            "host_env_file",
            CheckStatus.PASS,
            "required host variables are present; values were not printed",
        ),
        values,
    )


def iter_checkpoint_values(value: Any, prefix: str = "config") -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            location = f"{prefix}.{key}"
            if isinstance(child, str) and "checkpoint" in key.lower():
                entries.append((location, child))
            else:
                entries.extend(iter_checkpoint_values(child, location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            entries.extend(iter_checkpoint_values(child, f"{prefix}[{index}]"))
    return entries


def resolve_local_path(raw_path: str) -> Path | None:
    home = os.environ.get("HOME") or str(Path.home())
    portable = re.sub(r"\$(?:\{HOME\}|HOME(?![A-Za-z0-9_]))", lambda _: home, raw_path)
    expanded = os.path.expandvars(portable)
    if ENV_PATTERN.search(expanded):
        return None
    return Path(expanded).expanduser()


def check_checkpoint(label: str, raw_path: str) -> CheckResult:
    resolved = resolve_local_path(raw_path)
    if resolved is None:
        return CheckResult("checkpoint", label, CheckStatus.FAIL, "path has unresolved variables")
    try:
        non_empty = resolved.is_dir() and next(resolved.iterdir(), None) is not None
    except OSError:
        non_empty = False
    if non_empty:
        return CheckResult(
            "checkpoint",
            label,
            CheckStatus.PRESENT,
            "non-empty directory is present; checkpoint/processors compatibility is not checked",
        )
    return CheckResult(
        "checkpoint", label, CheckStatus.MISSING, "non-empty checkpoint directory is missing"
    )


def camera_path(value: Any) -> Path | None:
    if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
        return Path(f"/dev/video{value}")
    if isinstance(value, str) and value:
        return Path(value).expanduser()
    return None


def check_camera(label: str, value: Any) -> CheckResult:
    path = camera_path(value)
    if path is None:
        return CheckResult("camera", label, CheckStatus.FAIL, "camera identifier is not configured")
    if os.name == "nt":
        return CheckResult(
            "camera",
            label,
            CheckStatus.NOT_CHECKED,
            "Windows video-device inspection is unavailable; no device was opened",
        )
    try:
        is_device = stat.S_ISCHR(path.stat().st_mode)
        readable = os.access(path, os.R_OK)
    except OSError:
        is_device = False
        readable = False
    if is_device and readable:
        return CheckResult(
            "camera",
            label,
            CheckStatus.PRESENT,
            "readable video device is present; camera role and stream are not checked",
        )
    return CheckResult(
        "camera", label, CheckStatus.MISSING, "readable video character device is missing"
    )


def check_can_interface(interface: str) -> CheckResult:
    try:
        available = {name for _, name in socket.if_nameindex()}
    except OSError:
        return CheckResult(
            "can",
            "can_interface",
            CheckStatus.NOT_CHECKED,
            "network interface inventory is unavailable",
        )
    if interface not in available:
        return CheckResult("can", "can_interface", CheckStatus.MISSING, "interface is missing")

    link_root = Path("/sys/class/net") / interface
    link_type = link_root / "type"
    if link_type.is_file():
        try:
            if link_type.read_text(encoding="ascii").strip() != "280":
                return CheckResult(
                    "can",
                    "can_interface",
                    CheckStatus.FAIL,
                    "interface exists but is not reported as CAN",
                )
            state_path = link_root / "operstate"
            state = (
                state_path.read_text(encoding="ascii").strip()
                if state_path.is_file()
                else "unknown"
            )
        except OSError:
            return CheckResult(
                "can", "can_interface", CheckStatus.NOT_CHECKED, "interface type is unreadable"
            )
        return CheckResult(
            "can",
            "can_interface",
            CheckStatus.PRESENT,
            f"CAN interface is present (state={state}); bitrate and bus traffic are not checked",
        )
    return CheckResult(
        "can",
        "can_interface",
        CheckStatus.PRESENT,
        "interface is present; CAN link type, bitrate and bus traffic are not checked",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only software or deployment prerequisite presence checks."
    )
    parser.add_argument(
        "--profile",
        choices=("software", "deployment"),
        default="deployment",
        help="software excludes hardware/checkpoint presence checks",
    )
    parser.add_argument(
        "--config",
        default="configs/dual_act/dual_act.example.yaml",
        help="YAML deployment config to inspect",
    )
    parser.add_argument("--env-file", default=".env", help="local host environment file")
    parser.add_argument(
        "--package-manifest",
        default=str(DEFAULT_PACKAGE_MANIFEST),
        help="required Python distribution names",
    )
    parser.add_argument(
        "--checkpoint",
        action="append",
        default=[],
        help="additional local checkpoint directory; may be repeated",
    )
    parser.add_argument(
        "--package",
        action="append",
        default=[],
        help="additional Python distribution to check; may be repeated",
    )
    parser.add_argument("--camera", action="append", default=[], help="additional camera device")
    parser.add_argument("--can-interface", help="override the configured CAN interface")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return non-zero when any selected prerequisite is incomplete",
    )
    return parser


def run_checks(args: argparse.Namespace) -> dict[str, Any]:
    results = [check_python()]
    manifest_result, manifest_packages = load_package_manifest(Path(args.package_manifest))
    results.append(manifest_result)
    packages = list(dict.fromkeys((*manifest_packages, *args.package)))
    results.extend(check_packages(packages))

    config_result, config = inspect_config(Path(args.config))
    results.append(config_result)

    if args.profile == "deployment":
        env_result, host_env = inspect_env_file(Path(args.env_file))
        results.append(env_result)

        checkpoints: list[tuple[str, str]] = []
        if config is not None:
            checkpoints.extend(iter_checkpoint_values(config))
        if host_env is not None and host_env.get("CHECKPOINT_PATH"):
            checkpoints.append(("host_env.CHECKPOINT_PATH", host_env["CHECKPOINT_PATH"]))
        checkpoints.extend(
            (f"cli_checkpoint_{index}", value)
            for index, value in enumerate(args.checkpoint, start=1)
        )
        if checkpoints:
            results.extend(check_checkpoint(label, value) for label, value in checkpoints)
        else:
            results.append(
                CheckResult(
                    "checkpoint", "checkpoint", CheckStatus.MISSING, "no checkpoint is configured"
                )
            )

        configured_cameras: list[tuple[str, Any]] = []
        if host_env is not None:
            configured_cameras.extend(
                (key.lower(), host_env[key])
                for key in ("FRONT_CAMERA", "WRIST_CAMERA")
                if host_env.get(key)
            )
        elif config is not None:
            configured_cameras.extend(
                (key, config[key]) for key in ("front_camera", "wrist_camera") if key in config
            )
        configured_cameras.extend(
            (f"cli_camera_{index}", value) for index, value in enumerate(args.camera, start=1)
        )
        if configured_cameras:
            results.extend(check_camera(label, value) for label, value in configured_cameras)
        else:
            results.append(
                CheckResult("camera", "camera", CheckStatus.MISSING, "no camera is configured")
            )

        configured_can = args.can_interface
        if configured_can is None and host_env is not None:
            configured_can = host_env.get("CAN_INTERFACE")
        if configured_can is None and config is not None:
            configured_can = str(config.get("can_interface", "")) or None
        if configured_can is None:
            results.append(
                CheckResult("can", "can_interface", CheckStatus.MISSING, "not configured")
            )
        else:
            results.append(check_can_interface(configured_can))

    summary = {status.value.lower(): 0 for status in CheckStatus}
    for result in results:
        summary[result.status.value.lower()] += 1
    incomplete = sum(result.status not in ACCEPTED_STATUSES for result in results)
    return {
        "tool": "environment_check",
        "profile": args.profile,
        "read_only": True,
        "overall_status": "PASS" if incomplete == 0 else "INCOMPLETE",
        "deployment_evidence_status": "NOT_VERIFIED",
        "summary": {**summary, "total": len(results), "incomplete": incomplete},
        "checks": [result.as_dict() for result in results],
    }


def print_human(report: dict[str, Any]) -> None:
    print(f"Piper prerequisite check (read-only, profile={report['profile']})")
    for result in report["checks"]:
        print(
            f"{result['status']:<12} {result['category']:<10} {result['name']}: {result['detail']}"
        )
    summary = report["summary"]
    print(f"overall={report['overall_status']} incomplete={summary['incomplete']}")
    print("Presence checks are not hardware replay or policy compatibility evidence.")


def main() -> int:
    args = build_parser().parse_args()
    report = run_checks(args)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 1 if args.strict and report["overall_status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
