#!/usr/bin/env python3
"""Validate public manual hashes and the sanitized DROID evidence manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate() -> dict[str, Any]:
    assets = load_yaml(REPO_ROOT / "configs/reference/publication_assets.yaml")
    droid = load_yaml(REPO_ROOT / "configs/reference/droid_sample_manifest.yaml")
    manuals = assets.get("manuals")
    if assets.get("license") != "CC-BY-4.0" or not isinstance(manuals, list):
        raise ValueError("manual publication license or inventory is invalid")
    if len(manuals) != 9:
        raise ValueError("exactly nine public manuals are required")
    checked: list[str] = []
    for item in manuals:
        path = REPO_ROOT / item["path"]
        if not path.is_file() or path.suffix.lower() != ".pdf":
            raise ValueError(f"manual is missing: {item['path']}")
        if sha256(path) != item["sha256"]:
            raise ValueError(f"manual hash mismatch: {item['path']}")
        if int(item["pages"]) <= 0:
            raise ValueError(f"invalid page count: {item['path']}")
        checked.append(item["path"])

    selection = droid["selection"]
    observed = droid["observed_sample"]
    if (
        selection["success_episodes"] + selection["failure_episodes"]
        != selection["downloaded_episodes"]
    ):
        raise ValueError("DROID status counts do not match downloaded episode count")
    if len(observed["episode_lengths"]) != selection["downloaded_episodes"]:
        raise ValueError("DROID episode length count is inconsistent")
    if sum(observed["episode_lengths"]) != observed["total_timesteps"]:
        raise ValueError("DROID timestep total is inconsistent")
    if droid["privacy"]["raw_data_published"] is not False:
        raise ValueError("raw DROID data must not be published")
    return {
        "status": "PASS",
        "manuals": len(checked),
        "droid_episodes": selection["downloaded_episodes"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate()
    print(json.dumps(report, ensure_ascii=False) if args.json else "publication assets: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
