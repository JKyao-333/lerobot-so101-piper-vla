from copy import deepcopy

import pytest

from robot_learning.config import ConfigError, load_yaml, validate_manual_reference_config


def reference_config() -> dict:
    return load_yaml("configs/reference/manual_reference.yaml")


def test_manual_reference_profile_is_valid() -> None:
    validate_manual_reference_config(reference_config())


def test_reference_profile_does_not_claim_hardware_measurement() -> None:
    config = reference_config()
    assert config["provenance"]["hardware_measured"] is False


def test_control_rates_must_match_dataset_rate() -> None:
    config = deepcopy(reference_config())
    config["smolvla_async"]["control_fps"] = 10
    with pytest.raises(ConfigError, match="control rate must match"):
        validate_manual_reference_config(config)


def test_chunk_duration_must_match_actions_and_rate() -> None:
    config = deepcopy(reference_config())
    config["smolvla_async"]["nominal_chunk_duration_s"] = 4
    with pytest.raises(ConfigError, match="chunk duration"):
        validate_manual_reference_config(config)


def test_all_openvla_suites_are_required() -> None:
    config = deepcopy(reference_config())
    del config["openvla_libero"]["suites"]["long"]
    with pytest.raises(ConfigError, match="OpenVLA suites"):
        validate_manual_reference_config(config)


@pytest.mark.parametrize(
    "forbidden_key",
    ["success_rate", "measured_latency", "hardware_verified", "measured_gpu"],
)
def test_manual_profile_cannot_claim_measured_results(forbidden_key: str) -> None:
    config = deepcopy(reference_config())
    config["results"] = {forbidden_key: "not allowed"}
    with pytest.raises(ConfigError, match="cannot claim measured results"):
        validate_manual_reference_config(config)
