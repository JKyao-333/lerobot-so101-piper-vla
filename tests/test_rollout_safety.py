import pytest

from robot_learning.dual_act.rollout import DualActRollout, MockRobot
from robot_learning.dual_act.state_machine import Stage
from robot_learning.safety.action_filter import ActionFilter, ActionLimits, UnsafeActionError
from tests.test_dual_act_state_machine import machine


def test_first_invalid_action_aborts() -> None:
    state, _, _ = machine()
    robot = MockRobot()
    action_filter = ActionFilter(ActionLimits((-1.0,), (1.0,), (0.5,)))
    rollout = DualActRollout(state, robot, action_filter, execute_robot=True)
    state.start()

    with pytest.raises(UnsafeActionError):
        rollout.step()

    assert state.stage is Stage.ABORTED
    assert robot.stopped
    assert robot.sent_actions == []
