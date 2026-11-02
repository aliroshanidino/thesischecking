#!/usr/bin/env bash
# Run a short command on the HPC inside src/ with the project venv active.
# Usage: tools/remote.sh <cmd...>          e.g. tools/remote.sh pytest -q
# Long jobs go through tools/submit.sh instead (they must survive a dropped connection).
set -euo pipefail
source "$(dirname "$0")/hpc.env"
[ $# -ge 1 ] || { echo "usage: $0 <cmd...>" >&2; exit 2; }
ssh -o BatchMode=yes "$HPC" "cd $HPC_ROOT/src && source $HPC_VENV/bin/activate && export PYTHONPATH=$HPC_ROOT/src OMP_NUM_THREADS=\${OMP_NUM_THREADS:-$DEFAULT_THREADS} && $*"
