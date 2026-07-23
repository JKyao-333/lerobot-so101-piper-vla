#!/usr/bin/env python3
"""Run the dual-skill state machine in mock, hardware dry-run, or explicit execution mode."""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

from robot_learning.config import load_yaml, require_path, validate_dual_act_config
from robot_learning.dual_act.lerobot_adapter import LerobotPiperAdapter
from robot_learning.dual_act.rollout import DualActRollout, MockRobot
from robot_learning.dual_act.skill_runtime import SkillRuntime
from robot_learning.dual_act.state_machine import DualActStateMachine, Stage
from robot_learning.safety.action_filter import ActionFilter, ActionLimits


class MockPolicy:
    def __init__(self, action_dim: int) -> None:
        self.action_dim = action_dim
        self.reset_count = 0

    def reset(self) -> None:
        self.reset_count += 1

    def select_action(self, observation: Any) -> tuple[float, ...]:
        del observation
        return (0.0,) * self.action_dim


def mock_skill(name: str, action_dim: int) -> SkillRuntime:
    return SkillRuntime(
        policy=MockPolicy(action_dim),
        preprocess=lambda value: value,
        postprocess=lambda value: value,
        checkpoint_path=Path(f"mock_{name}"),
        task_name=f"mock {name}",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/dual_act/dual_act.example.yaml")
    parser.add_argument(
        "--hardware", action="store_true", help="connect Piper but keep action send disabled"
    )
    parser.add_argument(
        "--execute-robot", action="store_true", help="explicitly enable safe action transmission"
    )
    parser.add_argument(
        "--auto-confirm-mock",
        action="store_true",
        help="confirm the handoff non-interactively; accepted only without --hardware",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.execute_robot and not args.hardware:
        raise SystemExit("--execute-robot requires --hardware")
    if args.auto_confirm_mock and args.hardware:
        raise SystemExit("--auto-confirm-mock is forbidden with --hardware")
    config = load_yaml(args.config)
    validate_dual_act_config(config)
    config_allows_execution = bool(require_path(config, "allow_robot_execution"))
    if args.execute_robot and not config_allows_execution:
        raise SystemExit(
            "robot execution requires both allow_robot_execution=true in the config "
            "and --execute-robot on the command line"
        )
    execute_robot = bool(args.execute_robot and config_allows_execution)
    limits = ActionLimits(
        tuple(float(v) for v in require_path(config, "safety.lower_bounds")),
        tuple(float(v) for v in require_path(config, "safety.upper_bounds")),
        tuple(float(v) for v in require_path(config, "safety.max_step_delta")),
    )
    action_filter = ActionFilter(limits)

    adapter: LerobotPiperAdapter | None = None
    if args.hardware:
        print(
            "Hardware mode: emergency stop must be reachable; "
            "workspace and cameras must be checked."
        )
        adapter = LerobotPiperAdapter(
            can_interface=str(config.get("can_interface", "can0")),
            bitrate=int(config.get("bitrate", 1_000_000)),
            front_camera=config.get("front_camera", 0),
            wrist_camera=config.get("wrist_camera", 2),
            device=str(config.get("device", "cuda")),
            execute_robot=execute_robot,
        )
        adapter.connect()
        skill_a = adapter.load_skill(
            require_path(config, "skills.a.checkpoint"), require_path(config, "skills.a.task")
        )
        skill_b = adapter.load_skill(
            require_path(config, "skills.b.checkpoint"), require_path(config, "skills.b.task")
        )
        robot = adapter
    else:
        action_dim = int(require_path(config, "safety.action_dim"))
        skill_a, skill_b = mock_skill("a", action_dim), mock_skill("b", action_dim)
        robot = MockRobot()

    machine = DualActStateMachine(
        skill_a,
        skill_b,
        skill_a_timeout_s=float(require_path(config, "skills.a.timeout_s")),
        skill_b_timeout_s=float(require_path(config, "skills.b.timeout_s")),
        handoff_timeout_s=float(require_path(config, "handoff_timeout_s")),
        total_timeout_s=float(require_path(config, "total_timeout_s")),
    )
    rollout = DualActRollout(machine, robot, action_filter, execute_robot=execute_robot)
    completion_a = float(require_path(config, "skills.a.completion_s"))
    completion_b = float(require_path(config, "skills.b.completion_s"))
    period = 1.0 / float(require_path(config, "control_hz"))

    try:
        machine.start()
        stage_started = time.monotonic()
        while machine.stage not in {Stage.DONE, Stage.ABORTED}:
            tick = time.monotonic()
            if machine.stage is Stage.SKILL_A:
                rollout.step()
                if tick - stage_started >= completion_a or not args.hardware:
                    machine.complete_skill_a()
                    stage_started = time.monotonic()
            elif machine.stage is Stage.WAIT_CONFIRM:
                robot.stop()
                if args.auto_confirm_mock:
                    print("mock handoff auto-confirmed (hardware execution is disabled)")
                    answer = "yes"
                else:
                    answer = input(
                        "Confirm skill B after inspecting the handoff (Enter=yes, q=abort): "
                    )
                if answer.strip().lower() in {"", "y", "yes", "n", "next"}:
                    machine.confirm_handoff()
                    stage_started = time.monotonic()
                else:
                    machine.abort("operator rejected handoff")
            elif machine.stage is Stage.SKILL_B:
                rollout.step()
                if tick - stage_started >= completion_b or not args.hardware:
                    machine.complete_skill_b()
            time.sleep(max(0.0, period - (time.monotonic() - tick)))
    except (KeyboardInterrupt, EOFError):
        rollout.stop("operator interrupt or non-interactive handoff")
    except Exception:
        rollout.stop("unhandled exception")
        raise
    finally:
        try:
            robot.stop()
        finally:
            if adapter is not None:
                adapter.disconnect()
    print(f"final stage: {machine.stage.name}")
    return 0 if machine.stage is Stage.DONE else 1


if __name__ == "__main__":
    raise SystemExit(main())
