#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute-robot" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute-robot]"
for name in CHECKPOINT_PATH TASK_TEXT; do require_env "$name"; done
require_cmd lerobot-rollout
[[ -d "$CHECKPOINT_PATH" ]] || die "checkpoint directory not found"
front="${FRONT_CAMERA:-0}"; wrist="${WRIST_CAMERA:-2}"
cameras="{front: {type: opencv, index_or_path: ${front}, width: 640, height: 480, fps: 30},wrist: {type: opencv, index_or_path: ${wrist}, width: 640, height: 480, fps: 30}}"
cmd=(lerobot-rollout --strategy.type=base --policy.path="$CHECKPOINT_PATH"
  --robot.type=piper --robot.can_interface="${CAN_INTERFACE:-can0}" --robot.bitrate="${CAN_BITRATE:-1000000}"
  --robot.include_gripper=true --robot.use_degrees=false --robot.cameras="$cameras"
  --task="$TASK_TEXT" --duration="${DURATION_S:-20}")
printf '%s\n' 'Default is dry-run.' 'Confirm emergency stop, clear workspace, stable cameras, and low-speed validation.'
episodes="${ROLLOUT_EPISODES:-1}"
[[ "$episodes" =~ ^[1-9][0-9]*$ ]] || die "ROLLOUT_EPISODES must be a positive integer"
if [[ "$execute" == "true" ]]; then
  log_file="${LOG_FILE:-logs/smolvla_sync.log}"
  mkdir -p "$(dirname "$log_file")"
  print_command "${cmd[@]}"
  for ((episode = 1; episode <= episodes; episode++)); do
    printf 'starting supervised rollout episode %s/%s\n' "$episode" "$episodes" | tee -a "$log_file"
    "${cmd[@]}" 2>&1 | tee -a "$log_file"
  done
else
  print_command "${cmd[@]}"
  printf 'dry-run: %s episode(s) were not executed.\n' "$episodes"
fi
