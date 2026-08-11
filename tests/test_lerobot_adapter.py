import logging
from types import SimpleNamespace

import pytest

from robot_learning.dual_act.lerobot_adapter import LerobotPiperAdapter


class FakeInterface:
    def __init__(
        self, *, fail_hold: bool = False, status: dict[str, float] | None = None
    ) -> None:
        self.piper = object()
        self.min_pos = [-180.0] * 6 + [0.0]
        self.max_pos = [180.0] * 6 + [70.0]
        self.fail_hold = fail_hold
        self.status = status
        self.hold_calls: list[tuple[list[float], float | None]] = []

    def get_status_deg(self) -> dict[str, float]:
        if self.status is not None:
            return self.status
        return {**{f"joint_{index}.pos": 10.0 for index in range(1, 7)}, "gripper.pos": 5.0}

    def set_joint_positions_deg(self, joints: list[float], gripper: float | None) -> None:
        if self.fail_hold:
            raise RuntimeError("fake hold failure")
        self.hold_calls.append((joints, gripper))


class FakeRobot:
    def __init__(self, interface: FakeInterface) -> None:
        self._iface = interface
        self.is_connected = False
        self.disconnected = False
        self.disconnect_count = 0
        self.connect_error: Exception | None = None
        self.sent: list[dict[str, float]] = []
        self.action_features = {"action": True}
        self.observation_features = {"observation": True}
        self.config = SimpleNamespace(
            joint_names=[f"joint_{index}" for index in range(1, 7)],
            joint_signs=[-1, 1, 1, -1, 1, -1],
            joint_aliases={},
            include_gripper=True,
            use_degrees=False,
        )

    def send_action(self, action: dict[str, float]) -> None:
        self.sent.append(action)

    def connect(self) -> None:
        if self.connect_error is not None:
            raise self.connect_error

    def disconnect(self) -> None:
        self.disconnected = True
        self.disconnect_count += 1


def adapter_with(interface: FakeInterface) -> LerobotPiperAdapter:
    adapter = object.__new__(LerobotPiperAdapter)
    adapter._robot = FakeRobot(interface)
    adapter.execute_robot = True
    adapter._control_connected = True
    adapter._last_safe_action = None
    adapter._disconnect_completed = False
    adapter.dataset_features = None
    adapter.action_names = tuple([f"joint_{index}.pos" for index in range(1, 7)] + ["gripper.pos"])
    return adapter


def test_hold_does_not_depend_on_camera_connection() -> None:
    interface = FakeInterface()
    adapter = adapter_with(interface)
    assert adapter._robot.is_connected is False
    assert adapter.hold_current_pose_best_effort()
    assert len(interface.hold_calls) == 1


def test_hold_prefers_measured_current_pose() -> None:
    interface = FakeInterface()
    adapter = adapter_with(interface)
    adapter._last_safe_action = {"joint_1.pos": 0.0, "gripper.pos": 50.0}
    assert adapter.stop()
    joints, gripper = interface.hold_calls[0]
    assert joints == [10.0] * 6
    assert gripper == 5.0


def test_hold_falls_back_to_last_safe_action() -> None:
    interface = FakeInterface(status={})
    adapter = adapter_with(interface)
    adapter._last_safe_action = {
        **{f"joint_{index}.pos": 0.0 for index in range(1, 7)},
        "gripper.pos": 50.0,
    }
    assert adapter.hold_current_pose_best_effort()
    joints, gripper = interface.hold_calls[0]
    assert joints == [0.0] * 6
    assert gripper == 35.0


def test_hold_returns_false_without_measurement_or_fallback(caplog) -> None:
    adapter = adapter_with(FakeInterface(status={}))
    with caplog.at_level(logging.ERROR):
        assert not adapter.hold_current_pose_best_effort()
    assert "unable to construct hold command" in caplog.text


def test_hold_failure_is_reported(caplog) -> None:
    adapter = adapter_with(FakeInterface(fail_hold=True))
    with caplog.at_level(logging.ERROR):
        assert not adapter.hold_current_pose_best_effort()
    assert "best-effort Piper hold failed" in caplog.text


def test_disconnect_clears_control_connected() -> None:
    adapter = adapter_with(FakeInterface())
    adapter.disconnect()
    assert not adapter._control_connected
    assert adapter._robot.disconnected


def test_adapter_disconnect_is_idempotent() -> None:
    adapter = adapter_with(FakeInterface())
    adapter.disconnect()
    adapter.disconnect()
    assert adapter._robot.disconnect_count == 1


def test_connect_failure_disconnects_partial_resources() -> None:
    adapter = adapter_with(FakeInterface())
    adapter._robot.connect_error = RuntimeError("partial connect failure")
    adapter._feature_builder = lambda features, kind: features
    with pytest.raises(RuntimeError, match="partial connect failure"):
        adapter.connect()
    assert adapter._robot.disconnect_count == 1
    assert not adapter._control_connected


def test_action_feature_failure_disconnects_adapter() -> None:
    adapter = adapter_with(FakeInterface())

    def fail_features(features, kind):
        del features, kind
        raise RuntimeError("feature construction failed")

    adapter._feature_builder = fail_features
    with pytest.raises(RuntimeError, match="feature construction failed"):
        adapter.connect()
    assert adapter._robot.disconnect_count == 1
    assert not adapter._control_connected


def test_last_safe_action_is_recorded() -> None:
    adapter = adapter_with(FakeInterface())
    action = [0.0] * 7
    adapter.send_action(action)
    assert adapter._last_safe_action == dict(zip(adapter.action_names, action, strict=True))


def test_adapter_expands_checkpoint_path(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MODEL_ROOT", str(tmp_path))
    assert LerobotPiperAdapter.resolve_checkpoint_path("$MODEL_ROOT/model") == tmp_path / "model"
