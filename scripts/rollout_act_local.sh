#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute-robot" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute-robot]"
for name in CHECKPOINT_PATH TASK_TEXT; do require_env "$name"; done
require_cmd lerobot-rollout
[[ -d "$CHECKPOINT_PATH" ]] || die "checkpoint directory not found"

printf '%s\n' \
  'SAFETY CHECK: physical emergency stop is reachable.' \
  'SAFETY CHECK: workspace is clear of people, cables, glass, liquids, and sharp objects.' \
  'SAFETY CHECK: camera positions match data collection.' \
  'SAFETY CHECK: begin with a low-speed or dry-run validation.'

front="${FRONT_CAMERA:-0}"; wrist="${WRIST_CAMERA:-2}"
cameras="{front: {type: opencv, index_or_path: ${front}, width: 640, height: 480, fps: 30},wrist: {type: opencv, index_or_path: ${wrist}, width: 640, height: 480, fps: 30}}"
cmd=(lerobot-rollout --strategy.type=base --policy.path="$CHECKPOINT_PATH"
  --robot.type=piper --robot.can_interface="${CAN_INTERFACE:-can0}" --robot.bitrate="${CAN_BITRATE:-1000000}"
  --robot.include_gripper=true --robot.use_degrees=false --robot.cameras="$cameras"
  --task="$TASK_TEXT" --duration="${DURATION_S:-20}")
episodes="${ROLLOUT_EPISODES:-1}"
[[ "$episodes" =~ ^[1-9][0-9]*$ ]] || die "ROLLOUT_EPISODES must be a positive integer"
print_command "${cmd[@]}"
printf 'episodes: %s (each invocation is separately supervised)\n' "$episodes"
if [[ "$execute" == "true" ]]; then
  for ((episode = 1; episode <= episodes; episode++)); do
    printf 'starting supervised rollout episode %s/%s\n' "$episode" "$episodes"
    "${cmd[@]}"
  done
else
  printf 'dry-run: no robot action was sent.\n'
fi
