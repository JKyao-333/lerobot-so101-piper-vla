#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute-robot" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute-robot]"
for name in POLICY_SERVER_URL CHECKPOINT_PATH TASK_TEXT; do require_env "$name"; done
require_cmd python
front="${FRONT_CAMERA:-0}"; wrist="${WRIST_CAMERA:-2}"
cameras="{camera1: {type: opencv, index_or_path: ${front}, width: 640, height: 480, fps: 30},camera2: {type: opencv, index_or_path: ${wrist}, width: 640, height: 480, fps: 30}}"
cmd=(python -m lerobot.async_inference.robot_client --server_address="$POLICY_SERVER_URL"
  --robot.type=piper --robot.can_interface="${CAN_INTERFACE:-can0}" --robot.bitrate="${CAN_BITRATE:-1000000}"
  --robot.include_gripper=true --robot.use_degrees=false --robot.cameras="$cameras"
  --task="$TASK_TEXT" --policy_type=smolvla --pretrained_name_or_path="$CHECKPOINT_PATH"
  --policy_device="${POLICY_DEVICE:-cuda}" --client_device="${CLIENT_DEVICE:-cpu}"
  --fps="${CONTROL_FPS:-15}" --actions_per_chunk="${ACTIONS_PER_CHUNK:-50}"
  --chunk_size_threshold="${CHUNK_THRESHOLD:-0.5}" --aggregate_fn_name="${AGGREGATE_FN:-weighted_average}")
printf 'Network inference is not a safety-rated real-time control channel. Timeout or tunnel loss requires physical supervision and immediate stop.\n'
run_if_enabled "$execute" "${cmd[@]}"

