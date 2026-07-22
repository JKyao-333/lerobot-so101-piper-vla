from pathlib import Path

import pytest

from robot_learning.dual_act.skill_runtime import SkillRuntime
from robot_learning.dual_act.state_machine import DualActStateMachine, InvalidTransition, Stage


class Policy:
    def __init__(self) -> None:
        self.resets = 0

    def reset(self) -> None:
        self.resets += 1

    def select_action(self, value):
        return value


def runtime(policy: Policy) -> SkillRuntime:
    return SkillRuntime(policy, lambda x: x, lambda x: x, Path("mock"), "mock")


def machine(clock=lambda: 0.0):
    a, b = Policy(), Policy()
    return DualActStateMachine(
        runtime(a), runtime(b),
        skill_a_timeout_s=10,
        skill_b_timeout_s=10,
        handoff_timeout_s=5,
        total_timeout_s=30,
        clock=clock,
    ), a, b


def test_required_stage_sequence_and_manual_handoff() -> None:
    state, _, _ = machine()
    assert state.stage is Stage.INIT
    state.start()
    assert state.stage is Stage.SKILL_A
    state.complete_skill_a()
    assert state.stage is Stage.WAIT_CONFIRM
    state.confirm_handoff()
    assert state.stage is Stage.SKILL_B
    state.complete_skill_b()
    assert state.stage is Stage.DONE


def test_skill_b_cannot_start_without_confirmation() -> None:
    state, _, _ = machine()
    state.start()
    with pytest.raises(InvalidTransition):
        state.confirm_handoff()
    assert state.stage is Stage.SKILL_A


def test_stage_timeout_aborts() -> None:
    now = [0.0]
    state, _, _ = machine(clock=lambda: now[0])
    state.start()
    now[0] = 10.0
    assert state.check_timeouts()
    assert state.stage is Stage.ABORTED


def test_abort_is_available_from_wait_confirm() -> None:
    state, _, _ = machine()
    state.start()
    state.complete_skill_a()
    state.abort("operator stop")
    assert state.stage is Stage.ABORTED

