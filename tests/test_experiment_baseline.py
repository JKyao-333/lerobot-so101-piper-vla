from copy import deepcopy
from pathlib import Path

import pytest

from robot_learning.config import ConfigError, load_yaml, validate_experiment_baseline


def baseline_config() -> dict:
    return load_yaml("configs/reference/measured_experiment_baseline.yaml")


def test_experiment_baseline_provenance_is_valid() -> None:
    validate_experiment_baseline(baseline_config())


def test_source_experiment_is_marked_completed() -> None:
    source = baseline_config()["provenance"]["source_experiment"]
    assert source["hardware_operated"] is True
    assert source["robot_teleoperation_completed"] is True
    assert source["dataset_recording_completed"] is True
    assert source["training_completed"] is True
    assert source["evaluation_completed"] is True
    assert source["rollout_completed"] is True


def test_current_revision_hardware_replay_is_false() -> None:
    revision = baseline_config()["provenance"]["repository_revision"]
    assert revision["offline_validated"] is True
    assert revision["mock_validated"] is True
    assert revision["ci_validated"] is True
    assert revision["hardware_replayed_on_current_commit"] is False


def test_ci_without_hardware_does_not_negate_source_experiment() -> None:
    provenance = baseline_config()["provenance"]
    assert provenance["source_experiment"]["hardware_operated"] is True
    assert provenance["repository_revision"]["hardware_replayed_on_current_commit"] is False


def test_experiment_baseline_does_not_require_performance_metrics() -> None:
    config = baseline_config()
    assert "results" not in config
    validate_experiment_baseline(config)


def test_metric_requires_evidence_metadata() -> None:
    config = deepcopy(baseline_config())
    config["results"] = {"success_rate": 0.8}
    with pytest.raises(ConfigError, match="requires evidence metadata"):
        validate_experiment_baseline(config)


def test_metric_with_evidence_metadata_is_allowed() -> None:
    config = deepcopy(baseline_config())
    config["results"] = {
        "success_rate": 0.8,
        "evidence_path": "private/evaluation.json",
        "evaluation_date": "2026-07-01",
        "episodes_or_tasks": 10,
        "source_record": "source experiment record",
    }
    validate_experiment_baseline(config)


def test_control_rates_must_match_dataset_rate() -> None:
    config = deepcopy(baseline_config())
    config["smolvla_async"]["control_fps"] = 10
    with pytest.raises(ConfigError, match="control rate must match"):
        validate_experiment_baseline(config)


def test_chunk_duration_must_match_actions_and_rate() -> None:
    config = deepcopy(baseline_config())
    config["smolvla_async"]["nominal_chunk_duration_s"] = 4
    with pytest.raises(ConfigError, match="chunk duration"):
        validate_experiment_baseline(config)


def test_all_openvla_suites_are_required() -> None:
    config = deepcopy(baseline_config())
    del config["openvla_libero"]["suites"]["long"]
    with pytest.raises(ConfigError, match="OpenVLA suites"):
        validate_experiment_baseline(config)


@pytest.mark.parametrize(
    "forbidden_key",
    [
        "invented_success_rate",
        "invented_latency",
        "invented_loss",
        "industrial_grade",
        "production_verified",
        "safety_certified",
    ],
)
def test_experiment_baseline_rejects_unsupported_claims(forbidden_key: str) -> None:
    config = deepcopy(baseline_config())
    config["results"] = {forbidden_key: "not allowed"}
    with pytest.raises(ConfigError, match="unsupported claims"):
        validate_experiment_baseline(config)


def test_use_degrees_false_documented_as_normalized() -> None:
    root = Path(__file__).resolve().parents[1]
    documents = [
        root / "README.md",
        root / "docs/measured_experiment_baseline.md",
        root / "docs/safety.md",
        root / "docs/dual_act_long_horizon.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in documents)
    assert "use_degrees=false" in combined
    assert "normalized" in combined
    assert "归一化" in combined
    assert "radians/normalized mode" not in combined
    assert "not a hardware joint-angle limit" in combined
