#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute]"
for name in SSH_HOST SSH_PORT SSH_USER REMOTE_CHECKPOINT_PATH LOCAL_CHECKPOINT_PATH; do require_env "$name"; done
require_cmd scp
cmd=(scp -r -P "$SSH_PORT" "${SSH_USER}@${SSH_HOST}:${REMOTE_CHECKPOINT_PATH}" "$LOCAL_CHECKPOINT_PATH")
run_if_enabled "$execute" "${cmd[@]}"

