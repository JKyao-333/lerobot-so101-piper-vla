#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
if [[ "${1:-}" == "--execute" ]]; then
  execute=true
  shift
fi
[[ $# -eq 0 ]] || die "usage: $0 [--execute]"

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"

python_bin="${PYTHON_BIN:-python3}"
venv_dir="${VENV_DIR:-.venv}"
venv_python="$venv_dir/bin/python"

if [[ "$execute" == "true" ]]; then
  [[ "$(uname -s)" == "Linux" ]] || die "software bootstrap execution requires Linux"
  require_cmd "$python_bin"
  require_cmd git
  "$python_bin" - <<'PY'
import sys
if sys.version_info < (3, 12):
    raise SystemExit("Python 3.12 or newer is required by the pinned LeRobot runtime")
PY
fi

run_if_enabled "$execute" "$python_bin" -m venv "$venv_dir"
run_if_enabled "$execute" "$venv_python" -m pip install --upgrade pip
run_if_enabled "$execute" "$venv_python" -m pip install -r requirements/robot-runtime.txt
run_if_enabled "$execute" "$venv_python" -m pip install -e '.[dev]'
run_if_enabled "$execute" "$venv_python" scripts/environment_check.py \
  --profile software --strict

if [[ "$execute" == "true" ]]; then
  printf 'software environment installed; hardware and checkpoints remain unverified.\n'
else
  printf 'dry-run: no virtual environment was created and no package was downloaded.\n'
fi
