#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute]"
for name in SMOLVLA_BASE SMOLVLM_PATH DATASET_ROOT DATASET_REPO_ID OUTPUT_DIR; do require_env "$name"; done
require_cmd lerobot-train
[[ -d "$SMOLVLA_BASE" && -d "$SMOLVLM_PATH" && -d "$DATASET_ROOT" ]] || die "base model, VLM, and dataset must be local directories"

if [[ "${QUANTIZATION_ENABLE:-false}" == "true" ]]; then
  die "quantized SmolVLA training is not exposed by the verified LeRobot 0.6.1 config; refusing an invented flag"
fi
if [[ "${OFFLINE_MODE:-true}" == "true" ]]; then
  export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1
fi

rename_map='{"observation.images.front":"observation.images.camera1","observation.images.wrist":"observation.images.camera2"}'
cmd=(lerobot-train --dataset.root="$DATASET_ROOT" --dataset.repo_id="$DATASET_REPO_ID"
  --policy.path="$SMOLVLA_BASE" --policy.device="${DEVICE:-cuda}"
  --policy.vlm_model_name="$SMOLVLM_PATH" --policy.load_vlm_weights=true
  --policy.empty_cameras="${EMPTY_CAMERAS:-1}" --rename_map="$rename_map"
  --output_dir="$OUTPUT_DIR" --job_name="${JOB_NAME:-smolvla_piper}"
  --env_eval_freq=0 --wandb.enable=false --policy.push_to_hub=false)
[[ -n "${BATCH_SIZE:-}" ]] && cmd+=(--batch_size="$BATCH_SIZE")
[[ -n "${LEARNING_RATE:-}" ]] && cmd+=(--policy.optimizer_lr="$LEARNING_RATE")
[[ -n "${MAX_STEPS:-}" ]] && cmd+=(--steps="$MAX_STEPS")
[[ -n "${SAVE_STEPS:-}" ]] && cmd+=(--save_freq="$SAVE_STEPS")
[[ -n "${NUM_WORKERS:-}" ]] && cmd+=(--num_workers="$NUM_WORKERS")
if [[ "${LORA_ENABLE:-false}" == "true" ]]; then
  cmd+=(--peft.method_type=LORA --peft.r="${LORA_RANK:-16}")
fi
[[ -n "${RESUME_CHECKPOINT:-}" ]] && cmd+=(--resume=true --checkpoint_path="$RESUME_CHECKPOINT")
run_if_enabled "$execute" "${cmd[@]}"

