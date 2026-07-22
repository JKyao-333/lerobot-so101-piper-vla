#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute]"
for name in DATASET_ROOT DATASET_REPO_ID OUTPUT_DIR; do require_env "$name"; done
require_cmd lerobot-train

cmd=(lerobot-train --dataset.root="$DATASET_ROOT" --dataset.repo_id="$DATASET_REPO_ID"
  --policy.type=act --output_dir="$OUTPUT_DIR" --policy.device="${DEVICE:-cuda}"
  --wandb.enable="${WANDB_ENABLE:-false}" --policy.push_to_hub=false)
[[ -n "${TRAIN_STEPS:-}" ]] && cmd+=(--steps="$TRAIN_STEPS")
[[ -n "${BATCH_SIZE:-}" ]] && cmd+=(--batch_size="$BATCH_SIZE")
[[ -n "${SAVE_FREQ:-}" ]] && cmd+=(--save_freq="$SAVE_FREQ")
[[ -n "${RESUME_CHECKPOINT:-}" ]] && cmd+=(--resume=true --checkpoint_path="$RESUME_CHECKPOINT")
run_if_enabled "$execute" "${cmd[@]}"

