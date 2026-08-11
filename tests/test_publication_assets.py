from pathlib import Path

import yaml

from scripts.validate_publication_assets import validate

ROOT = Path(__file__).resolve().parents[1]


def test_publication_assets_validate() -> None:
    assert validate() == {"status": "PASS", "manuals": 9, "droid_episodes": 10}


def test_droid_manifest_is_sanitized_and_bounded() -> None:
    manifest = yaml.safe_load(
        (ROOT / "configs/reference/droid_sample_manifest.yaml").read_text(encoding="utf-8")
    )
    assert manifest["source"]["evidence_class"] == "upstream_public_dataset"
    assert manifest["user_work"]["classification"] == "user_executed_dataset_engineering"
    assert manifest["privacy"]["raw_data_published"] is False
    serialized = str(manifest).lower()
    for forbidden in ("robot_serial:", "user_id:", "scene_id:", "uuid:"):
        assert forbidden not in serialized
