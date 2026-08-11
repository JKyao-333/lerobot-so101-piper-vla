#!/usr/bin/env python3
"""Sanitize a log or fail when tracked repository text contains private patterns."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from robot_learning.logging_utils import contains_sensitive_text, sanitize_text

TEXT_SUFFIXES = {".md", ".py", ".sh", ".toml", ".yaml", ".yml", ".txt", ".example"}
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}
PATTERN_FIXTURES = {
    Path("src/robot_learning/logging_utils.py"),
    Path("scripts/sanitize_logs.py"),
    Path("tests/test_log_sanitization.py"),
}
PUBLIC_REFERENCE_LITERALS = (
    "/root/autodl-tmp/checkpoints/smolvla_piper_test/020000/pretrained_model",
    "/root/autodl-tmp/huggingface/SmolVLM2-500M-Video-Instruct",
    "/root/autodl-tmp/checkpoints/smolvla_piper_test",
    "/root/autodl-tmp/huggingface/smolvla_base",
    "/root/autodl-tmp/eval_logs/openvla",
)


def contains_unapproved_sensitive_text(text: str) -> bool:
    """Ignore only exact, documented public paths while retaining the broad scanner."""

    candidate = text
    for literal in PUBLIC_REFERENCE_LITERALS:
        candidate = candidate.replace(literal, "<PUBLIC_EXPERIMENT_PATH>")
    return contains_sensitive_text(candidate)


def repository_findings(root: Path) -> list[str]:
    findings: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.relative_to(root) in PATTERN_FIXTURES:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"Makefile", ".gitignore"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if contains_unapproved_sensitive_text(text):
            findings.append(str(path.relative_to(root)))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?")
    parser.add_argument("output", nargs="?")
    parser.add_argument("--stdin", action="store_true")
    parser.add_argument("--check-repository", metavar="ROOT")
    args = parser.parse_args()

    if args.check_repository:
        findings = repository_findings(Path(args.check_repository))
        if findings:
            for finding in findings:
                print(f"sensitive pattern: {finding}", file=sys.stderr)
            return 1
        print("secret pattern scan: clean")
        return 0

    if args.stdin:
        sys.stdout.write(sanitize_text(sys.stdin.read()))
        return 0
    if not args.input or not args.output:
        parser.error("provide INPUT OUTPUT, --stdin, or --check-repository ROOT")
    source = Path(args.input)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(sanitize_text(source.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"sanitized log written to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
