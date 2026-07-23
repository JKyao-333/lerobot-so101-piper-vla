import math

import pytest

from robot_learning.safety.action_filter import ActionFilter, ActionLimits, UnsafeActionError


@pytest.fixture
def action_filter() -> ActionFilter:
    return ActionFilter(ActionLimits((-10.0, -10.0, 0.0), (10.0, 10.0, 100.0), (2.0, 2.0, 4.0)))


def test_dimension_error_is_rejected(action_filter: ActionFilter) -> None:
    with pytest.raises(UnsafeActionError, match="dimension"):
        action_filter.apply([1.0, 2.0])


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_non_finite_action_is_rejected(action_filter: ActionFilter, bad: float) -> None:
    with pytest.raises(UnsafeActionError, match="NaN or Inf"):
        action_filter.apply([bad, 0.0, 0.0])


def test_absolute_joint_and_gripper_ranges_are_clipped(action_filter: ActionFilter) -> None:
    assert action_filter.apply([20.0, -20.0, 120.0]) == (10.0, -10.0, 100.0)


def test_step_delta_is_limited_after_absolute_clip(action_filter: ActionFilter) -> None:
    assert action_filter.apply([9.0, -9.0, 90.0], previous_action=[0.0, 0.0, 50.0]) == (
        2.0,
        -2.0,
        54.0,
    )


def test_action_filter_has_no_unused_error_threshold(action_filter: ActionFilter) -> None:
    assert not hasattr(action_filter, "max_consecutive_errors")
    assert not hasattr(action_filter, "consecutive_errors")
    assert not hasattr(action_filter, "tripped")
