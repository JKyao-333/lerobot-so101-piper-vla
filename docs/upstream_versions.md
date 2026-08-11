# Upstream versions inspected

| Upstream | Evidence in supplied local material | Public use |
| --- | --- | --- |
| LeRobot | package version 0.6.1; commit `e40b58a8dfa9e7b86918c374791599d070518d11`; origin `huggingface/lerobot` | CLI/API reference and external dependency |
| lerobot_robot_piper | package version 0.1.0; commit `abf721d9e88ac822b18cb3413a75bb8cc0e3b34f`; origin `AgRoboticsResearch/lerobot_robot_piper` | external Piper adapter |
| SmolVLA | implementation included in the inspected LeRobot tree; manuals reference the 0.6.0 workflow | external policy implementation |
| OpenVLA | no verifiable source checkout or commit supplied; only the manual command was inspected | wrapper uses only manual-confirmed arguments; record the installed revision before execution |
| LIBERO | no verifiable commit supplied | install in an isolated environment and record the actual revision privately |
| Piper SDK | required by the Piper adapter, but no exact revision supplied | external SDK under its own license |
| DROID | public raw dataset release 1.0.1; local subset inspected separately | upstream dataset; only downloader and sanitized structural summary are published |

The supplied LeRobot working tree contained an unrelated local modification. The commit above identifies its checked-out base; this repository does not copy or publish that modification.

The two verified source commits are encoded in [`requirements/robot-runtime.txt`](../requirements/robot-runtime.txt). The Piper SDK remains an adapter dependency without an evidence-backed exact revision; record the version resolved on the Robot PC rather than inventing a pin. OpenVLA/LIBERO are excluded from the hardware-runtime bootstrap because the supplied material did not establish source revisions for them.
