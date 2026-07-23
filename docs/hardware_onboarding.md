# Hardware onboarding

The software layout, configuration templates, workflow previews, MockRobot checks, and safety gates are prepared. A reproducer must install the pinned dependencies, replace host-specific values, connect the required hardware, and validate each level under direct supervision.

## Required hardware

- SO-101 leader
- Piper mechanical arm
- SocketCAN adapter
- front camera
- wrist camera
- Ubuntu robot PC
- physical emergency stop or the official Piper stop mechanism

## Values to verify locally

| Variable | Verify |
| --- | --- |
| `LEADER_PORT` | stable SO-101 serial device path |
| `CAN_INTERFACE` | actual SocketCAN interface name |
| `CAN_BITRATE` | Piper-required bitrate |
| `FRONT_CAMERA` | front camera identity and framing |
| `WRIST_CAMERA` | wrist camera identity and framing |
| `TASK_TEXT` | exact instruction matching the dataset/checkpoint |
| `DATASET_ROOT` | readable/writable local or cloud dataset path |
| `CHECKPOINT_PATH` | correct policy checkpoint and processors |
| `DEVICE` | installed CPU/CUDA device supported by the environment |

Also verify `/dev/video*` paths, dataset repository ids, all AutoDL/cloud paths, SSH endpoint and account, policy-server ports, camera resolution/FPS, and every installed upstream revision. Never commit local credentials or device serials.

## Staged validation

1. **Level 0 — CI/configuration:** install development dependencies and run `make validate`.
2. **Level 1 — workflow preview:** run `make workflow-dry-run`; confirm every command is a preview.
3. **Level 2 — device discovery:** run `scripts/check_robot_environment.sh` and inspect serial, video, and network devices without action execution.
4. **Level 3 — CAN/cameras:** verify camera roles and connectivity; preview `scripts/setup_can.sh`, then configure CAN only under local operator control.
5. **Level 4 — connection only:** connect Piper with action transmission disabled and verify observations, action dimensions, and checkpoints independently.
6. **Level 5 — supervised rollout:** clear the workspace, keep the physical stop reachable, use conservative speed, and enable one short rollout with direct supervision.
7. **Level 6 — full replay:** repeat recording, training/evaluation, checkpoint transfer, and rollout as a new current-commit result record.

Do not skip levels. Hardware execution is an explicit local action and dual ACT additionally requires both `allow_robot_execution=true` and `--execute-robot`.
