#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

output="${1:-}"
if [[ -n "$output" ]]; then
  mkdir -p "$(dirname "$output")"
  "$(dirname "$0")/check_robot_environment.sh" | python "$(dirname "$0")/sanitize_logs.py" --stdin >"$output"
  printf 'sanitized environment report written to %s\n' "$output"
else
  "$(dirname "$0")/check_robot_environment.sh" | python "$(dirname "$0")/sanitize_logs.py" --stdin
fi

