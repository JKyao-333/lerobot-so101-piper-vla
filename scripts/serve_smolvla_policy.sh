#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

execute=false
[[ "${1:-}" == "--execute" ]] && execute=true && shift
(($# == 0)) || die "usage: $0 [--execute]"
require_cmd python
host="${POLICY_SERVER_HOST:-127.0.0.1}"
port="${POLICY_SERVER_PORT:-8080}"
fps="${CONTROL_FPS:-15}"
timeout="${POLICY_OBS_TIMEOUT_S:-5}"
[[ "$host" == "127.0.0.1" || "$host" == "localhost" ]] || die "policy server must bind to loopback when used with the SSH tunnel"
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}" TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}" HF_DATASETS_OFFLINE="${HF_DATASETS_OFFLINE:-1}"
cmd=(python -m lerobot.async_inference.policy_server --host="$host" --port="$port" --fps="$fps" --obs_queue_timeout="$timeout")
printf 'The verified LeRobot server loads checkpoint/device from the client handshake; it has no batch-size CLI field.\n'
run_if_enabled "$execute" "${cmd[@]}"

