"""Deterministic action validation and clipping before robot transmission."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass


class UnsafeActionError(ValueError):
    """An action cannot be made safe without guessing its intended meaning."""


@dataclass(frozen=True)
class ActionLimits:
    lower_bounds: tuple[float, ...]
    upper_bounds: tuple[float, ...]
    max_step_delta: tuple[float, ...]

    def __post_init__(self) -> None:
        size = len(self.lower_bounds)
        if size == 0 or len(self.upper_bounds) != size or len(self.max_step_delta) != size:
            raise ValueError("all action limit vectors must have the same non-zero length")
        for index, (lower, upper, delta) in enumerate(
            zip(self.lower_bounds, self.upper_bounds, self.max_step_delta, strict=True)
        ):
            if not all(math.isfinite(value) for value in (lower, upper, delta)):
                raise ValueError(f"non-finite limit at index {index}")
            if lower > upper or delta <= 0:
                raise ValueError(f"invalid bounds or delta at index {index}")

    @property
    def action_dim(self) -> int:
        return len(self.lower_bounds)


class ActionFilter:
    """Reject malformed actions, then apply absolute and per-step bounds.

    Clipping cannot detect collisions, stalls, people, or unsafe scene geometry.
    """

    def __init__(self, limits: ActionLimits, max_consecutive_errors: int = 1) -> None:
        if max_consecutive_errors < 1:
            raise ValueError("max_consecutive_errors must be at least one")
        self.limits = limits
        self.max_consecutive_errors = max_consecutive_errors
        self.consecutive_errors = 0

    def _reject(self, message: str) -> None:
        self.consecutive_errors += 1
        raise UnsafeActionError(message)

    @property
    def tripped(self) -> bool:
        return self.consecutive_errors >= self.max_consecutive_errors

    def apply(
        self, action: Iterable[float], previous_action: Sequence[float] | None = None
    ) -> tuple[float, ...]:
        try:
            values = tuple(float(value) for value in action)
        except (TypeError, ValueError) as exc:
            self._reject(f"action contains a non-numeric value: {exc}")

        if len(values) != self.limits.action_dim:
            self._reject(
                f"action dimension {len(values)} does not match expected {self.limits.action_dim}"
            )
        if not all(math.isfinite(value) for value in values):
            self._reject("action contains NaN or Inf")

        previous: tuple[float, ...] | None = None
        if previous_action is not None:
            previous = tuple(float(value) for value in previous_action)
            if len(previous) != self.limits.action_dim or not all(
                math.isfinite(value) for value in previous
            ):
                self._reject("previous action is malformed or non-finite")

        bounded: list[float] = []
        for index, value in enumerate(values):
            value = min(
                max(value, self.limits.lower_bounds[index]), self.limits.upper_bounds[index]
            )
            if previous is not None:
                lower = previous[index] - self.limits.max_step_delta[index]
                upper = previous[index] + self.limits.max_step_delta[index]
                value = min(max(value, lower), upper)
                value = min(
                    max(value, self.limits.lower_bounds[index]), self.limits.upper_bounds[index]
                )
            bounded.append(value)

        self.consecutive_errors = 0
        return tuple(bounded)
