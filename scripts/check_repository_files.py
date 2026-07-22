#!/usr/bin/env python3
"""Reject large artifacts, datasets, videos, and model weights from the public tree."""

from __future__ import annotations

import argparse
from pathlib import Path

FORBIDDEN_SUFFIXES = {
    ".pt",
    ".pth",
    ".ckpt",
    ".safetensors",
    ".onnx",
    ".parquet",
    ".mp4",
    ".avi",
    ".mkv",
}
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--max-mb", type=float, default=20)
    args = parser.parse_args()
    root = Path(args.root)
    limit = int(args.max_mb * 1024 * 1024)
    failures: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        relative = path.relative_to(root)
        if path.stat().st_size > limit:
            failures.append(f"large file: {relative}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden artifact: {relative}")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"repository file scan: no files over {args.max_mb:g} MB and no forbidden artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
