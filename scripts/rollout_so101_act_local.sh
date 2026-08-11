#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute-robot" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute-robot]"
for name in SO101_FOLLOWER_PORT SO101_CHECKPOINT_PATH TASK_TEXT; do require_env "$name"; done
require_cmd_for_execute "$execute" lerobot-rollout
require_dir_for_execute "$execute" "$SO101_CHECKPOINT_PATH" checkpoint

front="${FRONT_CAMERA:-0}"
side="${SIDE_CAMERA:-${WRIST_CAMERA:-2}}"
cameras="{front: {type: opencv, index_or_path: ${front}, width: 640, height: 480, fps: 30},side: {type: opencv, index_or_path: ${side}, width: 640, height: 480, fps: 30}}"
cmd=(lerobot-rollout --strategy.type=base --policy.path="$SO101_CHECKPOINT_PATH"
  --robot.type=so101_follower --robot.port="$SO101_FOLLOWER_PORT"
  --robot.id="${SO101_FOLLOWER_ID:-so101_follower_01}" --robot.cameras="$cameras"
  --task="$TASK_TEXT" --duration="${DURATION_S:-20}")

printf '%s\n' \
  'SAFETY CHECK: physical stop and power cut-off are reachable.' \
  'SAFETY CHECK: checkpoint, calibration, camera roles and task text match collection.'
print_command "${cmd[@]}"
if [[ "$execute" == "true" ]]; then
  "${cmd[@]}"
else
  printf 'dry-run: no robot action was sent.\n'
fi
