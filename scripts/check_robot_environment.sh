#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

printf '== operating system ==\n'
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  printf '%s %s\n' "${NAME:-unknown}" "${VERSION_ID:-unknown}"
else
  printf 'unknown (expected Ubuntu robot host)\n'
fi

printf '\n== commands ==\n'
for command_name in python conda lerobot-record lerobot-rollout ip v4l2-ctl git; do
  if command -v "$command_name" >/dev/null 2>&1; then
    printf 'ok      %s\n' "$command_name"
  else
    printf 'missing %s\n' "$command_name"
  fi
done

printf '\n== robot interfaces ==\n'
leader_port="${LEADER_PORT:-}"
if [[ -n "$leader_port" && -e "$leader_port" ]]; then
  printf 'leader port exists (value intentionally not printed)\n'
else
  printf 'leader port not configured or not present\n'
fi
can_interface="${CAN_INTERFACE:-can0}"
ip -details link show "$can_interface" 2>/dev/null | sed -E 's/link\/ether [^ ]+/link\/ether <redacted>/' || printf 'CAN interface missing: %s\n' "$can_interface"

printf '\n== cameras ==\n'
camera_count=$(find /dev -maxdepth 1 -name 'video*' -type c 2>/dev/null | wc -l)
printf 'video device count: %s (device identities not collected)\n' "$camera_count"

printf '\n== compute and storage ==\n'
python --version 2>&1 || true
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true
else
  printf 'GPU check skipped: nvidia-smi unavailable\n'
fi
df -h . | tail -n 1 | awk '{print "workspace disk: size=" $2 ", available=" $4 ", use=" $5}'

printf '\n== upstream versions ==\n'
package_manifest="$(cd "$(dirname "$0")/.." && pwd)/configs/software/required_distributions.txt"
PACKAGE_MANIFEST="$package_manifest" python - <<'PY'
import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

manifest = Path(os.environ["PACKAGE_MANIFEST"])
packages = [
    line.strip()
    for line in manifest.read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.lstrip().startswith("#")
]
for package in packages:
    try:
        print(f"{package}: {version(package)}")
    except PackageNotFoundError:
        print(f"{package}: not installed")
PY
