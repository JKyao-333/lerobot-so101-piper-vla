#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute]"
for name in SMOLVLA_BASE SMOLVLM_PATH; do require_env "$name"; done
dataset_root="${SMOLVLA_DATASET_ROOT:-${DATASET_ROOT:-}}"
dataset_repo_id="${SMOLVLA_DATASET_REPO_ID:-${DATASET_REPO_ID:-}}"
output_dir="${SMOLVLA_OUTPUT_DIR:-${OUTPUT_DIR:-}}"
[[ -n "$dataset_root" ]] || die "SMOLVLA_DATASET_ROOT or DATASET_ROOT is required"
[[ -n "$dataset_repo_id" ]] || die "SMOLVLA_DATASET_REPO_ID or DATASET_REPO_ID is required"
[[ -n "$output_dir" ]] || die "SMOLVLA_OUTPUT_DIR or OUTPUT_DIR is required"
require_cmd_for_execute "$execute" lerobot-train
require_dir_for_execute "$execute" "$SMOLVLA_BASE" "base model"
require_dir_for_execute "$execute" "$SMOLVLM_PATH" VLM
require_dir_for_execute "$execute" "$dataset_root" dataset

if [[ "${QUANTIZATION_ENABLE:-false}" == "true" ]]; then
  die "quantized SmolVLA training is not exposed by the verified LeRobot 0.6.1 config; refusing an invented flag"
fi
if [[ "${OFFLINE_MODE:-true}" == "true" ]]; then
  export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1
fi

rename_map='{"observation.images.front":"observation.images.camera1","observation.images.wrist":"observation.images.camera2"}'
cmd=(lerobot-train --dataset.root="$dataset_root" --dataset.repo_id="$dataset_repo_id"
  --policy.path="$SMOLVLA_BASE" --policy.device="${DEVICE:-cuda}"
  --policy.vlm_model_name="$SMOLVLM_PATH" --policy.load_vlm_weights=true
  --policy.empty_cameras="${EMPTY_CAMERAS:-1}" --rename_map="$rename_map"
  --output_dir="$output_dir" --job_name="${JOB_NAME:-smolvla_piper}"
  --env_eval_freq=0 --wandb.enable=false --policy.push_to_hub=false)
batch_size="${SMOLVLA_BATCH_SIZE:-${BATCH_SIZE:-}}"
learning_rate="${SMOLVLA_LEARNING_RATE:-${LEARNING_RATE:-}}"
max_steps="${SMOLVLA_MAX_STEPS:-${MAX_STEPS:-}}"
save_freq="${SMOLVLA_SAVE_FREQ:-${SAVE_STEPS:-}}"
num_workers="${SMOLVLA_NUM_WORKERS:-${NUM_WORKERS:-}}"
[[ -n "$batch_size" ]] && cmd+=(--batch_size="$batch_size")
[[ -n "$learning_rate" ]] && cmd+=(--policy.optimizer_lr="$learning_rate")
[[ -n "$max_steps" ]] && cmd+=(--steps="$max_steps")
[[ -n "$save_freq" ]] && cmd+=(--save_freq="$save_freq")
[[ -n "$num_workers" ]] && cmd+=(--num_workers="$num_workers")
if [[ "${LORA_ENABLE:-false}" == "true" ]]; then
  cmd+=(--peft.method_type=LORA --peft.r="${LORA_RANK:-16}")
fi
[[ -n "${RESUME_CHECKPOINT:-}" ]] && cmd+=(--resume=true --checkpoint_path="$RESUME_CHECKPOINT")
run_if_enabled "$execute" "${cmd[@]}"
