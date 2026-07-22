"""Bind each skill policy to its own processors and metadata."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class SkillRuntime:
    policy: Any
    preprocess: Callable[[Any], Any]
    postprocess: Callable[[Any], Any]
    checkpoint_path: Path
    task_name: str

    def reset(self) -> None:
        reset = getattr(self.policy, "reset", None)
        if not callable(reset):
            raise TypeError("policy must expose reset()")
        reset()

    def predict(self, observation: Any) -> Any:
        processed = self.preprocess(observation)
        select_action = getattr(self.policy, "select_action", None)
        if not callable(select_action):
            raise TypeError("policy must expose select_action()")
        return self.postprocess(select_action(processed))
