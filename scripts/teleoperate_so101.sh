#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute-robot" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute-robot]"
for name in SO101_FOLLOWER_PORT LEADER_PORT; do require_env "$name"; done
require_cmd_for_execute "$execute" lerobot-teleoperate

front="${FRONT_CAMERA:-0}"
side="${SIDE_CAMERA:-${WRIST_CAMERA:-2}}"
cameras="{front: {type: opencv, index_or_path: ${front}, width: 640, height: 480, fps: 30},side: {type: opencv, index_or_path: ${side}, width: 640, height: 480, fps: 30}}"
cmd=(lerobot-teleoperate
  --robot.type=so101_follower --robot.port="$SO101_FOLLOWER_PORT"
  --robot.id="${SO101_FOLLOWER_ID:-so101_follower_01}" --robot.cameras="$cameras"
  --teleop.type=so101_leader --teleop.port="$LEADER_PORT"
  --teleop.id="${LEADER_ID:-so101_leader_01}")

printf '%s\n' \
  'SAFETY CHECK: verify voltage, polarity, cable direction and reachable power cut-off.' \
  'SAFETY CHECK: keep hands and cables outside joints, gripper and travel limits.'
run_if_enabled "$execute" "${cmd[@]}"
