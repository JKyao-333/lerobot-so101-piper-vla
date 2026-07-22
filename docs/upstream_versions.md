# Upstream versions inspected

| Upstream | Evidence in supplied local material | Public use |
| --- | --- | --- |
| LeRobot | package version 0.6.1; commit `e40b58a8dfa9e7b86918c374791599d070518d11`; origin `huggingface/lerobot` | CLI/API reference and external dependency |
| lerobot_robot_piper | package version 0.1.0; commit `abf721d9e88ac822b18cb3413a75bb8cc0e3b34f`; origin `AgRoboticsResearch/lerobot_robot_piper` | external Piper adapter |
| SmolVLA | implementation included in the inspected LeRobot tree; manuals reference the 0.6.0 workflow | external policy implementation |
| OpenVLA | no verifiable commit supplied | install in an isolated environment and record the actual revision privately |
| LIBERO | no verifiable commit supplied | install in an isolated environment and record the actual revision privately |
| Piper SDK | required by the Piper adapter, but no exact revision supplied | external SDK under its own license |

The supplied LeRobot working tree contained an unrelated local modification. The commit above identifies its checked-out base; this repository does not copy or publish that modification.

