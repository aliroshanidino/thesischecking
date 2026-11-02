#!/usr/bin/env bash
# Copy the small outputs of one run back to results/<run_dir> on the laptop.
# Only metrics.json, *.csv, figs/*.png, REPORT*.md, config.yaml, cmd.txt, git_commit.txt, each < 20 MB.
# Usage: tools/fetch.sh <run_dir relative to runs/>   e.g. tools/fetch.sh phase0/20261020-1430_s1_stdp
set -euo pipefail
source "$(dirname "$0")/hpc.env"
[ $# -eq 1 ] || { echo "usage: $0 <run_dir relative to runs/>" >&2; exit 2; }
run=${1#runs/}; run=${run%/}
top=$(git rev-parse --show-toplevel)
dest="$top/results/$run"
mkdir -p "$dest"
ssh -o BatchMode=yes "$HPC" bash -s -- "$HPC_ROOT/runs/$run" <<'EOF' | tar xf - -C "$dest"
cd "$1" || { echo "no such run: $1" >&2; exit 1; }
find . -type f -size -20M \( \
     \( ! -path './*/*' \( -name metrics.json -o -name '*.csv' -o -name 'REPORT*.md' -o -name config.yaml \
                           -o -name cmd.txt -o -name git_commit.txt \) \) \
  -o -path './figs/*.png' \) | tar cf - -T -
EOF
echo "fetched into results/$run:"
(cd "$dest" && find . -type f | sort | sed 's/^/  /')
