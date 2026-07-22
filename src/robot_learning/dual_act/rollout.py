"""Hardware-independent rollout coordinator with one action transmission gate."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from robot_learning.safety.action_filter import ActionFilter, UnsafeActionError

from .state_machine import DualActStateMachine, Stage

EXECUTE_ROBOT = False


class Robot(Protocol):
    def get_observation(self) -> Any: ...

    def send_action(self, action: Sequence[float]) -> None: ...

    def stop(self) -> None: ...


@dataclass
class MockRobot:
    observation: Any = field(default_factory=dict)
    sent_actions: list[tuple[float, ...]] = field(default_factory=list)
    stopped: bool = False

    def get_observation(self) -> Any:
        return self.observation

    def send_action(self, action: Sequence[float]) -> None:
        self.sent_actions.append(tuple(action))

    def stop(self) -> None:
        self.stopped = True


class DualActRollout:
    def __init__(
        self,
        machine: DualActStateMachine,
        robot: Robot,
        action_filter: ActionFilter,
        *,
        execute_robot: bool = EXECUTE_ROBOT,
    ) -> None:
        self.machine = machine
        self.robot = robot
        self.action_filter = action_filter
        self.execute_robot = execute_robot
        self.previous_action: tuple[float, ...] | None = None

    def step(self) -> tuple[float, ...] | None:
        if self.machine.check_timeouts():
            self.robot.stop()
            return None
        skill = self.machine.active_skill()
        if skill is None:
            return None
        try:
            proposed = skill.predict(self.robot.get_observation())
            safe = self.action_filter.apply(proposed, self.previous_action)
        except (Exception, UnsafeActionError) as exc:
            self.machine.abort(f"action failure: {exc}")
            self.robot.stop()
            raise
        self.previous_action = safe
        if self.execute_robot:
            self.robot.send_action(safe)
        return safe

    def stop(self, reason: str = "operator stop") -> None:
        self.machine.abort(reason)
        self.robot.stop()

    @property
    def safe_state(self) -> bool:
        return self.machine.stage in {Stage.DONE, Stage.ABORTED}
