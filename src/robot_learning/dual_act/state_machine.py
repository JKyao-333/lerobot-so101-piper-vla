"""Finite-state coordinator for two independently trained ACT skills."""

from __future__ import annotations

import time
from collections.abc import Callable
from enum import Enum, auto

from .skill_runtime import SkillRuntime


class Stage(Enum):
    INIT = auto()
    SKILL_A = auto()
    WAIT_CONFIRM = auto()
    SKILL_B = auto()
    DONE = auto()
    ABORTED = auto()


class InvalidTransition(RuntimeError):
    pass


class DualActStateMachine:
    def __init__(
        self,
        skill_a: SkillRuntime,
        skill_b: SkillRuntime,
        *,
        skill_a_timeout_s: float,
        skill_b_timeout_s: float,
        handoff_timeout_s: float,
        total_timeout_s: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        for name, value in (
            ("skill_a_timeout_s", skill_a_timeout_s),
            ("skill_b_timeout_s", skill_b_timeout_s),
            ("handoff_timeout_s", handoff_timeout_s),
            ("total_timeout_s", total_timeout_s),
        ):
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        self.skill_a = skill_a
        self.skill_b = skill_b
        self.timeouts = {
            Stage.SKILL_A: skill_a_timeout_s,
            Stage.WAIT_CONFIRM: handoff_timeout_s,
            Stage.SKILL_B: skill_b_timeout_s,
        }
        self.total_timeout_s = total_timeout_s
        self.clock = clock
        self.stage = Stage.INIT
        self.started_at: float | None = None
        self.stage_started_at: float | None = None
        self.abort_reason: str | None = None

    def _set_stage(self, stage: Stage) -> None:
        self.stage = stage
        self.stage_started_at = self.clock()

    def start(self) -> None:
        if self.stage is not Stage.INIT:
            raise InvalidTransition("a task can only start from INIT")
        self.skill_a.reset()
        self.skill_b.reset()
        self.started_at = self.clock()
        self._set_stage(Stage.SKILL_A)

    def complete_skill_a(self) -> None:
        if self.stage is not Stage.SKILL_A:
            raise InvalidTransition("skill A can only complete from SKILL_A")
        self._set_stage(Stage.WAIT_CONFIRM)

    def confirm_handoff(self) -> None:
        if self.stage is not Stage.WAIT_CONFIRM:
            raise InvalidTransition("handoff can only be confirmed from WAIT_CONFIRM")
        self.skill_b.reset()
        self._set_stage(Stage.SKILL_B)

    def complete_skill_b(self) -> None:
        if self.stage is not Stage.SKILL_B:
            raise InvalidTransition("skill B can only complete from SKILL_B")
        self._set_stage(Stage.DONE)

    def abort(self, reason: str) -> None:
        if self.stage not in {Stage.DONE, Stage.ABORTED}:
            self.abort_reason = reason
            self._set_stage(Stage.ABORTED)

    def active_skill(self) -> SkillRuntime | None:
        if self.stage is Stage.SKILL_A:
            return self.skill_a
        if self.stage is Stage.SKILL_B:
            return self.skill_b
        return None

    def check_timeouts(self) -> bool:
        if self.stage in {Stage.INIT, Stage.DONE, Stage.ABORTED}:
            return False
        now = self.clock()
        if self.started_at is not None and now - self.started_at >= self.total_timeout_s:
            self.abort("total task timeout")
            return True
        stage_timeout = self.timeouts[self.stage]
        if self.stage_started_at is not None and now - self.stage_started_at >= stage_timeout:
            self.abort(f"{self.stage.name.lower()} timeout")
            return True
        return False
