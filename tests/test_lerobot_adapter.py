import logging
from types import SimpleNamespace

from robot_learning.dual_act.lerobot_adapter import LerobotPiperAdapter


class FakeInterface:
    def __init__(self, *, fail_hold: bool = False) -> None:
        self.piper = object()
        self.min_pos = [-180.0] * 6 + [0.0]
        self.max_pos = [180.0] * 6 + [70.0]
        self.fail_hold = fail_hold
        self.hold_calls: list[tuple[list[float], float | None]] = []

    def get_status_deg(self) -> dict[str, float]:
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
        self.sent: list[dict[str, float]] = []
        self.config = SimpleNamespace(
            joint_names=[f"joint_{index}" for index in range(1, 7)],
            joint_signs=[-1, 1, 1, -1, 1, -1],
            joint_aliases={},
            include_gripper=True,
            use_degrees=False,
        )

    def send_action(self, action: dict[str, float]) -> None:
        self.sent.append(action)

    def disconnect(self) -> None:
        self.disconnected = True


def adapter_with(interface: FakeInterface) -> LerobotPiperAdapter:
    adapter = object.__new__(LerobotPiperAdapter)
    adapter._robot = FakeRobot(interface)
    adapter.execute_robot = True
    adapter._control_connected = True
    adapter._last_safe_action = None
    adapter.action_names = tuple([f"joint_{index}.pos" for index in range(1, 7)] + ["gripper.pos"])
    return adapter


def test_hold_does_not_depend_on_camera_connection() -> None:
    interface = FakeInterface()
    adapter = adapter_with(interface)
    assert adapter._robot.is_connected is False
    assert adapter.hold_current_pose_best_effort()
    assert len(interface.hold_calls) == 1


def test_hold_uses_control_channel_when_camera_is_down() -> None:
    interface = FakeInterface()
    adapter = adapter_with(interface)
    adapter._last_safe_action = {"joint_1.pos": 0.0, "gripper.pos": 50.0}
    assert adapter.stop()
    joints, gripper = interface.hold_calls[0]
    assert len(joints) == 6
    assert gripper == 35.0


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


def test_last_safe_action_is_recorded() -> None:
    adapter = adapter_with(FakeInterface())
    action = [0.0] * 7
    adapter.send_action(action)
    assert adapter._last_safe_action == dict(zip(adapter.action_names, action, strict=True))


def test_adapter_expands_checkpoint_path(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MODEL_ROOT", str(tmp_path))
    assert LerobotPiperAdapter.resolve_checkpoint_path("$MODEL_ROOT/model") == tmp_path / "model"
