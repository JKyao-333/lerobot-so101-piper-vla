#!/usr/bin/env bash
set -Eeuo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"
python_cmd="${PYTHON:-python}"

# Load the version-controlled experiment baseline without writing a local .env.
set -a
# shellcheck disable=SC1091
source .env.example
set +a

# OpenVLA is intentionally absent from this repository. These non-existent example
# roots are sufficient for preview mode, which must not inspect or create them.
export OPENVLA_ROOT="${OPENVLA_ROOT:-/opt/example/openvla}"
export LIBERO_ROOT="${LIBERO_ROOT:-/opt/example/libero}"

bash scripts/setup_robot_software.sh
bash scripts/setup_can.sh
bash scripts/teleoperate_so101.sh
bash scripts/record_so101_act.sh
bash scripts/record_piper_act.sh
bash scripts/train_act_autodl.sh
bash scripts/download_act_checkpoint.sh
bash scripts/rollout_act_local.sh
bash scripts/rollout_so101_act_local.sh
bash scripts/eval_openvla_libero.sh \
  --suite spatial \
  --checkpoint openvla/openvla-7b-finetuned-libero-spatial \
  --output-dir /tmp/openvla-preview
bash scripts/finetune_smolvla_piper.sh
bash scripts/rollout_smolvla_sync.sh
bash scripts/serve_smolvla_policy.sh
bash scripts/open_policy_ssh_tunnel.sh
bash scripts/run_smolvla_robot_client.sh
"$python_cmd" scripts/run_dual_act.py \
  --config configs/dual_act/dual_act.example.yaml \
  --auto-confirm-mock

printf 'workflow previews: passed without execute flags\n'
