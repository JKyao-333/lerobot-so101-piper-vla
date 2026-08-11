#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute-robot" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute-robot]"
for name in SO101_FOLLOWER_PORT LEADER_PORT TASK_TEXT SO101_DATASET_REPO_ID SO101_DATASET_ROOT; do
  require_env "$name"
done
require_cmd_for_execute "$execute" lerobot-record

front="${FRONT_CAMERA:-0}"
side="${SIDE_CAMERA:-${WRIST_CAMERA:-2}}"
cameras="{front: {type: opencv, index_or_path: ${front}, width: 640, height: 480, fps: 30},side: {type: opencv, index_or_path: ${side}, width: 640, height: 480, fps: 30}}"
cmd=(lerobot-record
  --robot.type=so101_follower --robot.port="$SO101_FOLLOWER_PORT"
  --robot.id="${SO101_FOLLOWER_ID:-so101_follower_01}" --robot.cameras="$cameras"
  --teleop.type=so101_leader --teleop.port="$LEADER_PORT"
  --teleop.id="${LEADER_ID:-so101_leader_01}"
  --dataset.repo_id="$SO101_DATASET_REPO_ID" --dataset.root="$SO101_DATASET_ROOT"
  --dataset.push_to_hub=false --dataset.num_episodes="${NUM_EPISODES:-50}"
  --dataset.single_task="$TASK_TEXT" --dataset.episode_time_s="${EPISODE_TIME_S:-30}"
  --dataset.reset_time_s="${RESET_TIME_S:-15}" --dataset.streaming_encoding=true
  --dataset.encoder_threads="${ENCODER_THREADS:-2}" --dataset.fps="${SO101_DATASET_FPS:-30}")
run_if_enabled "$execute" "${cmd[@]}"
