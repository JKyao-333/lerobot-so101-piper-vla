#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

suite=""; checkpoint=""; output_dir=""; center_crop=true; execute=false
while (($#)); do
  case "$1" in
    --suite) suite="$2"; shift 2 ;;
    --checkpoint) checkpoint="$2"; shift 2 ;;
    --output-dir) output_dir="$2"; shift 2 ;;
    --center-crop) center_crop="$2"; shift 2 ;;
    --execute) execute=true; shift ;;
    *) die "unknown argument: $1" ;;
  esac
done
[[ -n "$suite" && -n "$checkpoint" && -n "$output_dir" ]] || die "--suite, --checkpoint, and --output-dir are required"
case "$suite" in
  spatial) task_suite=libero_spatial ;;
  object) task_suite=libero_object ;;
  goal) task_suite=libero_goal ;;
  long) task_suite=libero_10 ;;
  *) die "suite must be spatial, object, goal, or long" ;;
esac
[[ "$center_crop" == "true" || "$center_crop" == "false" ]] || die "--center-crop must be true or false"
require_env OPENVLA_ROOT
require_env LIBERO_ROOT
if [[ "$execute" == "true" ]]; then
  [[ -d "$OPENVLA_ROOT" ]] || die "OPENVLA_ROOT is not a directory"
  [[ -d "$LIBERO_ROOT" ]] || die "LIBERO_ROOT is not a directory"
  if [[ ! -e "$checkpoint" && ! "$checkpoint" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
    die "checkpoint must be a local path or Hugging Face repository id"
  fi
  require_cmd python
  if [[ "${MUJOCO_GL:-}" != "egl" && -z "${DISPLAY:-}" ]]; then
    die "headless evaluation requires MUJOCO_GL=egl"
  fi
  python -c 'import libero, mujoco' >/dev/null || die "LIBERO or MuJoCo cannot be imported"
fi

run_dir="${output_dir%/}/${suite}_$(date +%Y%m%d_%H%M%S)"
log_file="$run_dir/evaluation.log"
cmd=(python "$OPENVLA_ROOT/experiments/robot/libero/run_libero_eval.py"
  --model_family openvla --pretrained_checkpoint "$checkpoint"
  --task_suite_name "$task_suite" --center_crop "$center_crop")
print_command "${cmd[@]}"
if [[ "$execute" == "true" ]]; then
  mkdir -p "$run_dir"
  {
    printf 'suite=%s\nwrapper_working_directory=%s\n' "$task_suite" "$(pwd)"
    "${cmd[@]}"
  } 2>&1 | tee "$log_file"
  printf 'wrapper console log: %s\n' "$log_file"
  printf 'Upstream artifact locations depend on the installed OpenVLA revision.\n'
  printf 'Do not publish a success rate until this log has been reviewed and sanitized.\n'
else
  printf 'dry-run: no simulation was started, no directory was created, and no metric was generated.\n'
fi
