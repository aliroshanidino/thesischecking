#!/usr/bin/env bash
# Session-start check on the laptop (replaces hpc_health.sh, DECISIONS D15): disk, work/ size vs cap, GPU, RAM,
# power source, running jobs. Exits non-zero when work/ is above the cap or the drive is nearly full.
set -uo pipefail
source "$(dirname "$0")/local.env"
status=0
work_mb=$(du -sm "$WORK" 2>/dev/null | cut -f1); work_mb=${work_mb:-0}
free_gb=$(df -BG "$WORK" | awk 'NR==2{gsub("G","",$4); print $4}')
echo "== work/: $(awk -v m=$work_mb 'BEGIN{printf "%.2f", m/1024}') GB of ${WORK_CAP_GB} GB cap | drive free: ${free_gb} GB =="
du -sm "$WORK"/* 2>/dev/null | awk -F'\t' '{n=$2; sub(".*/", "", n); printf "   %7d MB  %s\n", $1, n}'
echo "== raw data: $RAW =="   # (no du here: 20 GB / 12k files takes ~1 min on Windows)
echo "== GPU: $(nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu,utilization.gpu --format=csv,noheader 2>/dev/null || echo 'nvidia-smi not available') =="
powershell -NoProfile -Command "\$o = Get-CimInstance Win32_OperatingSystem; '== RAM: {0:N1} GB free of {1:N1} GB ==' -f (\$o.FreePhysicalMemory/1MB), (\$o.TotalVisibleMemorySize/1MB); \$b = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue; if (\$b) { '== power: {0}, battery {1}% ==' -f \$(if (\$b.BatteryStatus -eq 2) { 'on AC' } else { 'ON BATTERY' }), \$b.EstimatedChargeRemaining }"
running=$(find "$WORK/runs" -name .running 2>/dev/null | wc -l)
echo "== running jobs: $running =="
if [ "$work_mb" -gt $((WORK_CAP_GB * 1024)) ]; then echo "STOP: work/ is above ${WORK_CAP_GB} GB. Ask the user before writing more."; status=1; fi
if [ "${free_gb:-0}" -lt "$MIN_FREE_GB" ]; then echo "STOP: only ${free_gb} GB free on the drive."; status=1; fi
exit $status
