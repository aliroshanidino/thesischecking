#!/usr/bin/env bash
# Laptop GPU environment (DECISIONS D14): Python 3.12 venv in biovision-snn/.venv with
# torch 2.14.1 + torchvision 0.29.1 (CUDA 12.6 builds) and CuPy 14 for custom CUDA kernels (NVRTC, no MSVC).
# Other packages are pinned to the HPC versions (env/constraints-hpc.txt). Needs a direct internet connection.
set -euo pipefail
cd "$(dirname "$0")/.."
unset HTTPS_PROXY HTTP_PROXY https_proxy http_proxy
[ -x .venv/Scripts/python ] || py -3.12 -m venv .venv
PY=.venv/Scripts/python
$PY -m pip install --disable-pip-version-check -q --upgrade pip
$PY -m pip install --disable-pip-version-check --progress-bar off --timeout 60 --retries 10 \
    torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cu126
$PY -m pip install --disable-pip-version-check --progress-bar off --timeout 60 --retries 10 \
    -c env/constraints-hpc.txt -r env/requirements-nontorch.txt -r env/requirements-extra.txt "cupy-cuda12x[ctk]==14.2.0"
$PY -m pip install --disable-pip-version-check -q --no-deps -e third_party/SpykeTorch
$PY -m pip freeze --exclude-editable > env/requirements-lock-laptop.txt
$PY - <<'EOF'
import torch, cupy
print("torch", torch.__version__, "| CUDA", torch.version.cuda, "| GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NOT AVAILABLE")
print("cupy", cupy.__version__, "| devices:", cupy.cuda.runtime.getDeviceCount())
EOF
