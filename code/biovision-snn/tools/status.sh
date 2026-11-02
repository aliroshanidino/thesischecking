#!/usr/bin/env bash
# Our jobs on the HPC: running / finished runs of the last N days, last 20 log lines of running ones, load.
# Usage: tools/status.sh [days=3]
set -euo pipefail
source "$(dirname "$0")/hpc.env"
days=${1:-3}
ssh -o BatchMode=yes "$HPC" bash -s -- "$HPC_ROOT" "$days" <<'EOF'
root=$1; days=$2
echo "== load: $(cut -d' ' -f1-3 /proc/loadavg)  (cores: $(nproc))  RAM: $(free -g | awk '/Mem:/{print $7" GB available"}') =="
echo "== tmux sessions =="; tmux ls 2>/dev/null | grep '^bv_' || echo "  (none)"
echo "== runs touched in the last $days days =="
found=0
while IFS= read -r d; do
  found=1
  rel=${d#$root/runs/}
  if [ -f "$d/exit_code" ]; then
    state="finished (exit $(cat "$d/exit_code"))"
  elif [ -f "$d/pid" ] && kill -0 "$(cat "$d/pid")" 2>/dev/null; then
    state="RUNNING ($(cat "$d/threads" 2>/dev/null || echo ?) threads)"
  else
    state="no process, no exit code (crashed or killed?)"
  fi
  echo "-- $rel: $state"
  case "$state" in RUNNING*|no\ process*) tail -n 20 "$d/log.txt" 2>/dev/null | sed 's/^/     /' ;; esac
done < <(find "$root/runs" -mindepth 2 -maxdepth 2 -type d -mtime -"$days" 2>/dev/null | sort)
[ $found = 1 ] || echo "  (none)"
EOF
