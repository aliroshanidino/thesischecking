#!/usr/bin/env bash
# Install the project venv on the HPC from wheels already copied to $HPC_ROOT/wheels (CLAUDE.md 3.5 Step D).
# Run ON THE HPC:  bash $HPC_ROOT/src/env/install_offline.sh [requirements file, default env/requirements.txt]
# Writes $HPC_ROOT/requirements-lock.txt (copy it back to env/ on the laptop and commit it).
set -euo pipefail
HPC_ROOT=${HPC_ROOT:-/home/kut/biovision}
REQ=${1:-$HPC_ROOT/src/env/requirements.txt}
source "$HPC_ROOT/venv/bin/activate"
cd "$HPC_ROOT/src"
pip install --no-index --find-links "$HPC_ROOT/wheels" -r "$REQ"
pip install --no-index --no-deps --no-build-isolation -e "$HPC_ROOT/src/third_party/SpykeTorch"
pip check || true
pip freeze --exclude-editable > "$HPC_ROOT/requirements-lock.txt"
python - <<'EOF'
import sys, torch
print("python", sys.version.split()[0], "| torch", torch.__version__, "| threads", torch.get_num_threads())
import SpykeTorch.snn, SpykeTorch.functional  # noqa: F401  vendored package imports
print("SpykeTorch import OK")
EOF
