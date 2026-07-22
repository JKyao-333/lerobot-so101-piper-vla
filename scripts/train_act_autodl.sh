#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute]"
dataset_root="${ACT_DATASET_ROOT:-${DATASET_ROOT:-}}"
dataset_repo_id="${ACT_DATASET_REPO_ID:-${DATASET_REPO_ID:-}}"
output_dir="${ACT_OUTPUT_DIR:-${OUTPUT_DIR:-}}"
[[ -n "$dataset_root" ]] || die "ACT_DATASET_ROOT or DATASET_ROOT is required"
[[ -n "$dataset_repo_id" ]] || die "ACT_DATASET_REPO_ID or DATASET_REPO_ID is required"
[[ -n "$output_dir" ]] || die "ACT_OUTPUT_DIR or OUTPUT_DIR is required"
require_cmd_for_execute "$execute" lerobot-train

cmd=(lerobot-train --dataset.root="$dataset_root" --dataset.repo_id="$dataset_repo_id"
  --policy.type=act --output_dir="$output_dir" --policy.device="${DEVICE:-cuda}"
  --wandb.enable="${WANDB_ENABLE:-false}" --policy.push_to_hub=false)
[[ -n "${ACT_TRAIN_STEPS:-${TRAIN_STEPS:-}}" ]] && cmd+=(--steps="${ACT_TRAIN_STEPS:-$TRAIN_STEPS}")
act_batch_size="${ACT_BATCH_SIZE:-${BATCH_SIZE:-}}"
act_save_freq="${ACT_SAVE_FREQ:-${SAVE_FREQ:-}}"
[[ -n "$act_batch_size" ]] && cmd+=(--batch_size="$act_batch_size")
[[ -n "$act_save_freq" ]] && cmd+=(--save_freq="$act_save_freq")
[[ -n "${RESUME_CHECKPOINT:-}" ]] && cmd+=(--resume=true --checkpoint_path="$RESUME_CHECKPOINT")
run_if_enabled "$execute" "${cmd[@]}"
