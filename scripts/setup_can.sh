#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/_common.sh"

interface="${CAN_INTERFACE:-can0}"
bitrate="${CAN_BITRATE:-1000000}"
execute=false

while (($#)); do
  case "$1" in
    --interface) interface="$2"; shift 2 ;;
    --bitrate) bitrate="$2"; shift 2 ;;
    --execute) execute=true; shift ;;
    *) die "unknown argument: $1" ;;
  esac
done

[[ "$bitrate" =~ ^[0-9]+$ ]] || die "bitrate must be a positive integer"

if [[ "$execute" == "true" ]]; then
  require_cmd ip
  ip link show "$interface" >/dev/null 2>&1 || die "network interface does not exist: $interface"
  sudo ip link set "$interface" down || true
  sudo ip link set "$interface" type can bitrate "$bitrate"
  sudo ip link set "$interface" up
else
  print_command sudo ip link set "$interface" down
  print_command sudo ip link set "$interface" type can bitrate "$bitrate"
  print_command sudo ip link set "$interface" up
  printf 'dry-run: CAN configuration was not changed.\n'
fi
if command -v ip >/dev/null 2>&1 && ip link show "$interface" >/dev/null 2>&1; then
  ip -details link show "$interface"
else
  printf 'inspection skipped: %s is unavailable on this host.\n' "$interface"
fi
