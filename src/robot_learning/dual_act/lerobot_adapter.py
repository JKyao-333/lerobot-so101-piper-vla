"""Lazy bridge to upstream LeRobot and lerobot_robot_piper APIs.

No upstream source is copied here. Imports occur only when hardware mode is requested.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .skill_runtime import SkillRuntime


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

    def connect(self) -> None:
        self._robot.connect()
        actions = self._feature_builder(self._robot.action_features, "action")
        observations = self._feature_builder(self._robot.observation_features, "observation")
        self.dataset_features = {**actions, **observations}
        names = self.dataset_features.get("action", {}).get("names")
        if not names:
            raise RuntimeError("Piper action features do not expose ordered action names")
        self.action_names = tuple(str(name) for name in names)

    def disconnect(self) -> None:
        self._robot.disconnect()

    def get_observation(self) -> dict[str, Any]:
        return self._robot.get_observation()

    def send_action(self, action: Sequence[float]) -> None:
        if not self.execute_robot:
            return
        if len(action) != len(self.action_names):
            raise ValueError("safe action dimension does not match Piper action names")
        self._robot.send_action(dict(zip(self.action_names, action, strict=True)))

    def stop(self) -> None:
        if not self.execute_robot or not getattr(self._robot, "is_connected", False):
            return
        observation = self.get_observation()
        missing = set(self.action_names) - set(observation)
        if missing:
            raise RuntimeError(
                f"cannot issue hold command; missing observation keys: {sorted(missing)}"
            )
        self._robot.send_action({name: float(observation[name]) for name in self.action_names})

    def load_skill(self, checkpoint: str | Path, task_name: str) -> SkillRuntime:
        if self.dataset_features is None:
            raise RuntimeError("connect the robot before loading a skill")
        checkpoint_path = Path(checkpoint)
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
