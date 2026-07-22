#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute]"
for name in SSH_HOST SSH_PORT SSH_USER; do require_env "$name"; done
require_cmd ssh
local_port="${LOCAL_FORWARD_PORT:-8080}"
remote_port="${REMOTE_POLICY_PORT:-8080}"
cmd=(ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=15 -o ServerAliveCountMax=3
  -L "${local_port}:127.0.0.1:${remote_port}" -p "$SSH_PORT" "${SSH_USER}@${SSH_HOST}")
run_if_enabled "$execute" "${cmd[@]}"

