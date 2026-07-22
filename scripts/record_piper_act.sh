#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute] (configuration is supplied through environment variables)"

for name in LEADER_PORT TASK_TEXT DATASET_REPO_ID DATASET_ROOT; do require_env "$name"; done
require_cmd lerobot-record

can_interface="${CAN_INTERFACE:-can0}"
bitrate="${CAN_BITRATE:-1000000}"
front="${FRONT_CAMERA:-0}"
wrist="${WRIST_CAMERA:-2}"
episodes="${NUM_EPISODES:-1}"
episode_time="${EPISODE_TIME_S:-30}"
reset_time="${RESET_TIME_S:-15}"
dataset_fps="${DATASET_FPS:-15}"
cameras="{front: {type: opencv, index_or_path: ${front}, width: 640, height: 480, fps: 30},wrist: {type: opencv, index_or_path: ${wrist}, width: 640, height: 480, fps: 30}}"

cmd=(lerobot-record
  --robot.type=piper --robot.can_interface="$can_interface" --robot.bitrate="$bitrate"
  --robot.include_gripper=true --robot.use_degrees=false --robot.cameras="$cameras"
  --teleop.type=so101_leader --teleop.port="$LEADER_PORT" --teleop.id="${LEADER_ID:-so101_leader_example}"
  --dataset.repo_id="$DATASET_REPO_ID" --dataset.root="$DATASET_ROOT" --dataset.push_to_hub=false
  --dataset.num_episodes="$episodes" --dataset.single_task="$TASK_TEXT"
  --dataset.episode_time_s="$episode_time" --dataset.reset_time_s="$reset_time"
  --dataset.streaming_encoding=true --dataset.encoder_threads="${ENCODER_THREADS:-2}"
  --dataset.fps="$dataset_fps" --dataset.rgb_encoder.crf="${RGB_CRF:-20}")
run_if_enabled "$execute" "${cmd[@]}"

