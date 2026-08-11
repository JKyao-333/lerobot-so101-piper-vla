"""Hardware-independent rollout coordinator with one action transmission gate."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from robot_learning.safety.action_filter import ActionFilter

from .state_machine import DualActStateMachine, Stage

EXECUTE_ROBOT = False
logger = logging.getLogger(__name__)


class Robot(Protocol):
    def get_observation(self) -> Any: ...

    def send_action(self, action: Sequence[float]) -> None: ...

    def stop(self) -> bool | None: ...


@dataclass
class MockRobot:
    observation: Any = field(default_factory=dict)
    sent_actions: list[tuple[float, ...]] = field(default_factory=list)
    stopped: bool = False

    def get_observation(self) -> Any:
        return self.observation

    def send_action(self, action: Sequence[float]) -> None:
        self.sent_actions.append(tuple(action))

    def stop(self) -> bool:
        self.stopped = True
        return True


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

    def hold_best_effort(self, context: str) -> bool:
        try:
            result = self.robot.stop()
        except Exception:
            logger.exception("best-effort hold raised during %s", context)
            return False
        if result is False:
            logger.error("best-effort hold failed during %s", context)
            return False
        return True

    def step(self) -> tuple[float, ...] | None:
        if self.machine.check_timeouts():
            self.hold_best_effort("timeout")
            return None
        skill = self.machine.active_skill()
        if skill is None:
            return None
        try:
            proposed = skill.predict(self.robot.get_observation())
            safe = self.action_filter.apply(proposed, self.previous_action)
        except Exception as exc:
            self.machine.abort(f"action failure: {exc}")
            self.hold_best_effort("action failure")
            raise
        self.previous_action = safe
        if self.execute_robot:
            self.robot.send_action(safe)
        return safe

    def stop(self, reason: str = "operator stop") -> None:
        self.machine.abort(reason)
        self.hold_best_effort(reason)

    @property
    def safe_state(self) -> bool:
        return self.machine.stage in {Stage.DONE, Stage.ABORTED}
