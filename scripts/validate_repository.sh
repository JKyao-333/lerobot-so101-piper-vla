#!/usr/bin/env bash
set -Eeuo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"
python_cmd="${PYTHON:-python}"

"$python_cmd" -m compileall -q src scripts
while IFS= read -r -d '' script; do bash -n "$script"; done < <(find scripts -type f -name '*.sh' -print0)
"$python_cmd" - <<'PY'
from pathlib import Path
from robot_learning.config import (
    load_yaml,
    validate_dual_act_config,
    validate_manual_reference_config,
)

for path in Path("configs").rglob("*.yaml"):
    load_yaml(path)
validate_dual_act_config(load_yaml("configs/dual_act/dual_act.example.yaml"))
validate_manual_reference_config(load_yaml("configs/reference/manual_reference.yaml"))
print("configuration templates: valid")
PY
"$python_cmd" scripts/validate_reference_profile.py
PYTHON="$python_cmd" bash scripts/validate_workflow_previews.sh
"$python_cmd" -m pytest -q
"$python_cmd" scripts/sanitize_logs.py --check-repository .
"$python_cmd" scripts/check_repository_files.py --root . --max-mb 20
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git diff --check
fi
printf 'repository validation: passed\n'
