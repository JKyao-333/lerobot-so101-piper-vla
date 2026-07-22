"""Monotonic timeout watchdog used for stages and network responses."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol


class Stoppable(Protocol):
    def stop(self) -> None: ...


@dataclass
class Watchdog:
    timeout_s: float
    clock: Callable[[], float] = time.monotonic
    _deadline: float = field(init=False)

    def __post_init__(self) -> None:
        if self.timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self.reset()

    def reset(self) -> None:
        self._deadline = self.clock() + self.timeout_s

    def expired(self) -> bool:
        return self.clock() >= self._deadline

    @property
    def remaining_s(self) -> float:
        return max(0.0, self._deadline - self.clock())


@dataclass
class NetworkSafetyMonitor:
    """Convert a missing policy response into one idempotent robot stop."""

    watchdog: Watchdog
    stopped: bool = False

    def record_response(self) -> None:
        self.watchdog.reset()

    def enforce(self, robot: Stoppable) -> bool:
        if not self.stopped and self.watchdog.expired():
            robot.stop()
            self.stopped = True
        return self.stopped
