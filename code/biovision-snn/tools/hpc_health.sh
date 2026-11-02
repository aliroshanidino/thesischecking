#!/usr/bin/env bash
# Disk use per top-level folder of HPC_ROOT vs the cap, free disk, RAM and load.
# Exits non-zero when the project uses more than DISK_STOP_GB (then stop and ask the user).
# Usage: tools/hpc_health.sh
set -euo pipefail
source "$(dirname "$0")/hpc.env"
ssh -o BatchMode=yes "$HPC" bash -s -- "$HPC_ROOT" "$DISK_CAP_GB" "$DISK_STOP_GB" <<'EOF'
root=$1; cap=$2; stop=$3
[ -d "$root" ] || { echo "HPC_ROOT $root does not exist"; exit 3; }
echo "== $root (MB per folder) =="
du -s --block-size=1M "$root"/* "$root"/.[!.]* 2>/dev/null | sort -rn | awk '{printf "  %8d MB  %s\n", $1, $2}'
used_mb=$(du -s --block-size=1M "$root" | cut -f1)
used_gb=$(awk -v m="$used_mb" 'BEGIN{printf "%.2f", m/1024}')
echo "== project total: ${used_gb} GB  (stop at ${stop} GB, cap ${cap} GB) =="
echo "== disk free on filesystem: $(df -h "$root" | awk 'NR==2{print $4" free of "$2}') =="
echo "== RAM: $(free -g | awk '/Mem:/{print $7" GB available of "$2" GB"}') =="
echo "== load: $(cut -d' ' -f1-3 /proc/loadavg)  (cores: $(nproc)) =="
if awk -v u="$used_gb" -v s="$stop" 'BEGIN{exit !(u > s)}'; then
  echo "STOP: project uses ${used_gb} GB > ${stop} GB. Ask the user before writing more data."
  exit 1
fi
EOF
