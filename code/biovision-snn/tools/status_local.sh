#!/usr/bin/env bash
# Laptop jobs: runs touched in the last N days, state, last 20 log lines of running/crashed ones, GPU load.
# Usage: tools/status_local.sh [days=3]
set -uo pipefail
source "$(dirname "$0")/local.env"
days=${1:-3}
echo "== GPU: $(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader 2>/dev/null) =="
found=0
while IFS= read -r d; do
  found=1
  if [ -f "$d/exit_code" ]; then state="finished (exit $(cat "$d/exit_code"))"
  elif [ -f "$d/.running" ]; then state="RUNNING since $(date -r "$d/cmd.txt" +%H:%M)"
  else state="no exit code (crashed, killed or laptop slept?)"; fi
  echo "-- ${d#$WORK/runs/}: $state"
  case "$state" in RUNNING*|no\ exit*) tail -n 20 "$d/log.txt" 2>/dev/null | sed 's/^/     /' ;; esac
done < <(find "$WORK/runs" -mindepth 2 -maxdepth 2 -type d -mtime -"$days" 2>/dev/null | sort)
[ $found = 1 ] || echo "  (no runs in the last $days days)"
