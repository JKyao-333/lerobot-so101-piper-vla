"""Lazy bridge to upstream LeRobot and lerobot_robot_piper APIs.

No upstream source is copied here. Imports occur only when hardware mode is requested.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from robot_learning.config import resolve_config_path

from .skill_runtime import SkillRuntime

logger = logging.getLogger(__name__)


class LerobotPiperAdapter:
    def __init__(
        self,
        *,
        can_interface: str,
        bitrate: int,
        front_camera: int | str,
        wrist_camera: int | str,
        device: str,
        execute_robot: bool,
    ) -> None:
        try:
            import torch
            from lerobot.cameras.opencv import OpenCVCameraConfig
            from lerobot.policies.utils import make_robot_action
            from lerobot_robot_piper.config_piper import PiperConfig
            from lerobot_robot_piper.piper import Piper

            try:
                from lerobot.utils.feature_utils import hw_to_dataset_features
            except ImportError:
                from lerobot.datasets.utils import hw_to_dataset_features
        except ImportError as exc:
            raise RuntimeError(
                "hardware mode requires LeRobot and lerobot_robot_piper; "
                "install requirements/act.txt"
            ) from exc

        cameras = {
            "front": OpenCVCameraConfig(
                index_or_path=front_camera, width=640, height=480, fps=30, fourcc="MJPG"
            ),
            "wrist": OpenCVCameraConfig(
                index_or_path=wrist_camera, width=640, height=480, fps=30, fourcc="MJPG"
            ),
        }
        self._robot = Piper(
            PiperConfig(
                can_interface=can_interface,
                bitrate=bitrate,
                include_gripper=True,
                use_degrees=False,
                cameras=cameras,
            )
        )
        self._torch = torch
        self._make_robot_action = make_robot_action
        self._feature_builder = hw_to_dataset_features
        self.device = device
        self.execute_robot = execute_robot
        self.dataset_features: dict[str, Any] | None = None
        self.action_names: tuple[str, ...] = ()
        self._control_connected = False
        self._last_safe_action: dict[str, float] | None = None

    def connect(self) -> None:
        try:
            self._robot.connect()
        finally:
            self._control_connected = self._pinned_piper_control_interface() is not None
        actions = self._feature_builder(self._robot.action_features, "action")
        observations = self._feature_builder(self._robot.observation_features, "observation")
        self.dataset_features = {**actions, **observations}
        names = self.dataset_features.get("action", {}).get("names")
        if not names:
            raise RuntimeError("Piper action features do not expose ordered action names")
        self.action_names = tuple(str(name) for name in names)

    def disconnect(self) -> None:
        try:
            self._robot.disconnect()
        finally:
            self._control_connected = False

    def get_observation(self) -> dict[str, Any]:
        return self._robot.get_observation()

    def send_action(self, action: Sequence[float]) -> None:
        if not self.execute_robot:
            return
        if len(action) != len(self.action_names):
            raise ValueError("safe action dimension does not match Piper action names")
        command = dict(zip(self.action_names, action, strict=True))
        self._robot.send_action(command)
        self._last_safe_action = {name: float(value) for name, value in command.items()}

    def _pinned_piper_control_interface(self) -> Any | None:
        """Return the private control interface for pinned Piper commit abf721d9 only.

        This is the sole location that accesses Piper._iface. The private API is not
        treated as stable and every caller must handle an unavailable interface.
        """

        interface = getattr(self._robot, "_iface", None)
        if interface is None or getattr(interface, "piper", None) is None:
            return None
        return interface

    def _best_effort_hold_via_pinned_piper_adapter(self) -> bool:
        """Hold the latest safe/current pose through the pinned low-level interface."""

        interface = self._pinned_piper_control_interface()
        if interface is None:
            raise RuntimeError("pinned Piper control interface is unavailable")

        config = self._robot.config
        joint_names = list(config.joint_names)
        status = interface.get_status_deg()
        joints_hw_deg: list[float | None] = [
            float(status[f"joint_{index}.pos"]) if f"joint_{index}.pos" in status else None
            for index in range(1, len(joint_names) + 1)
        ]
        gripper_mm = (
            float(status["gripper.pos"])
            if config.include_gripper and "gripper.pos" in status
            else None
        )

        if self._last_safe_action:
            min_pos = getattr(interface, "min_pos", None)
            max_pos = getattr(interface, "max_pos", None)
            if not isinstance(min_pos, list) or not isinstance(max_pos, list):
                raise RuntimeError("pinned Piper limits are unavailable")
            aliases = dict(config.joint_aliases)
            joint_index = {name: index for index, name in enumerate(joint_names)}
            for key, raw_value in self._last_safe_action.items():
                if key == "gripper.pos":
                    if config.include_gripper:
                        value = float(raw_value)
                        if config.use_degrees:
                            gripper_mm = value
                        else:
                            value = max(0.0, min(100.0, value))
                            gripper_mm = min_pos[6] + (max_pos[6] - min_pos[6]) * value / 100.0
                    continue
                action_name = key.removesuffix(".pos")
                joint_name = aliases.get(action_name, action_name)
                if joint_name not in joint_index:
                    continue
                index = joint_index[joint_name]
                value = float(raw_value)
                if config.use_degrees:
                    oriented_deg = value
                else:
                    sign = config.joint_signs[index]
                    oriented_min = min_pos[index] if sign >= 0 else -max_pos[index]
                    oriented_max = max_pos[index] if sign >= 0 else -min_pos[index]
                    normalized = max(-100.0, min(100.0, value))
                    oriented_deg = oriented_min + (oriented_max - oriented_min) * (
                        (normalized + 100.0) / 200.0
                    )
                joints_hw_deg[index] = max(
                    min_pos[index],
                    min(max_pos[index], oriented_deg * config.joint_signs[index]),
                )

        if any(value is None for value in joints_hw_deg):
            raise RuntimeError("cannot construct a complete Piper hold command")
        interface.set_joint_positions_deg(
            [float(value) for value in joints_hw_deg if value is not None], gripper_mm
        )
        return True

    def hold_current_pose_best_effort(self) -> bool:
        """Best-effort position hold; this is not a physical emergency stop."""

        if not self.execute_robot:
            return True
        if not self._control_connected:
            logger.error("cannot hold Piper pose: control channel is not connected")
            return False
        try:
            return self._best_effort_hold_via_pinned_piper_adapter()
        except Exception:
            logger.exception("best-effort Piper hold failed")
            return False

    def stop(self) -> bool:
        """Protocol alias for best-effort position hold, not an emergency stop."""

        return self.hold_current_pose_best_effort()

    @staticmethod
    def resolve_checkpoint_path(checkpoint: str | Path) -> Path:
        return resolve_config_path(checkpoint)

    def load_skill(self, checkpoint: str | Path, task_name: str) -> SkillRuntime:
        if self.dataset_features is None:
            raise RuntimeError("connect the robot before loading a skill")
        checkpoint_path = self.resolve_checkpoint_path(checkpoint)
        if not checkpoint_path.is_dir():
            raise FileNotFoundError(f"checkpoint directory not found: {checkpoint_path}")
        from lerobot.policies import make_pre_post_processors
        from lerobot.policies.act import ACTPolicy
        from lerobot.policies.utils import build_inference_frame

        policy = ACTPolicy.from_pretrained(str(checkpoint_path))
        policy.to(self.device)
        policy.config.device = self.device
        policy.eval()
        upstream_preprocess, upstream_postprocess = make_pre_post_processors(
            policy_cfg=policy.config,
            pretrained_path=str(checkpoint_path),
            preprocessor_overrides={"device_processor": {"device": self.device}},
        )

        def preprocess(observation: dict[str, Any]) -> Any:
            frame = build_inference_frame(
                observation=observation,
                ds_features=self.dataset_features,
                device=self.device,
                robot_type="piper",
            )
            return upstream_preprocess(frame)

        def postprocess(action_tensor: Any) -> tuple[float, ...]:
            action_tensor = upstream_postprocess(action_tensor)
            action = self._make_robot_action(action_tensor, self.dataset_features)
            if set(action) != set(self.action_names):
                raise ValueError("policy action keys do not match Piper action features")
            return tuple(float(action[name]) for name in self.action_names)

        original_select_action = policy.select_action

        class InferencePolicy:
            def reset(self) -> None:
                policy.reset()

            def select_action(self, processed: Any) -> Any:
                with self_torch.inference_mode():
                    return original_select_action(processed)

        self_torch = self._torch
        return SkillRuntime(
            policy=InferencePolicy(),
            preprocess=preprocess,
            postprocess=postprocess,
            checkpoint_path=checkpoint_path,
            task_name=task_name,
        )
