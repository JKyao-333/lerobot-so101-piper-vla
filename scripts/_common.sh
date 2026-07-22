#!/usr/bin/env bash
set -Eeuo pipefail

die() { printf 'error: %s\n' "$*" >&2; exit 2; }
require_cmd() { command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"; }
require_env() { [[ -n "${!1:-}" ]] || die "required environment variable is empty: $1"; }
require_cmd_for_execute() {
  local enabled="$1"
  local command_name="$2"
  [[ "$enabled" == "true" ]] && require_cmd "$command_name"
  return 0
}
require_dir_for_execute() {
  local enabled="$1"
  local path="$2"
  local label="$3"
  [[ "$enabled" != "true" || -d "$path" ]] || die "$label directory not found: $path"
}

print_command() {
  printf 'preview:'
  printf ' %q' "$@"
  printf '\n'
}

run_if_enabled() {
  local enabled="$1"
  shift
  print_command "$@"
  if [[ "$enabled" == "true" ]]; then
    "$@"
  else
    printf 'dry-run: command was not executed; pass the documented execute flag to opt in.\n'
  fi
}
