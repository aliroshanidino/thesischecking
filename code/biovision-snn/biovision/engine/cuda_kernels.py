"""Custom CUDA kernels written with CuPy (compiled at runtime by NVRTC; no MSVC / CUDA Toolkit needed).

Optional: imported only on a machine with CuPy and a GPU (the laptop, DECISIONS D14). Every kernel has a
pure-PyTorch reference in ``engine/`` and a test that compares the two.

Tensors are shared with PyTorch through DLPack (no copies) and kernels run on PyTorch's current stream.
"""

from __future__ import annotations

import torch

from .spikes import NO_SPIKE

try:
    import cupy as cp
except ImportError:  # pragma: no cover - CPU-only machines (HPC)
    cp = None

_FIRST_CROSSING_SRC = r"""
extern "C" __global__
void first_crossing(const float* __restrict__ pot, const float* __restrict__ theta,
                    unsigned char* __restrict__ times, float* __restrict__ vfire,
                    const int T, const int C, const int HW) {
    // One thread per neuron. Non-leaky IF: the neuron fires at the first step with V(t) >= theta_c
    // (CLAUDE.md Section 4) and stays silent afterwards, so the scan stops at the first crossing.
    const long long n = (long long)C * HW;
    const long long i = (long long)blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    const float th = theta[i / HW];
    unsigned char t_out = 255;
    float v_out = 0.0f;
    for (int t = 0; t < T; ++t) {
        const float v = pot[(long long)t * n + i];
        if (v >= th) { t_out = (unsigned char)t; v_out = v; break; }
    }
    times[i] = t_out;
    vfire[i] = v_out;
}
"""

_kernels: dict[str, object] = {}


def available() -> bool:
    return cp is not None and torch.cuda.is_available()


def _kernel(name: str, src: str):
    if name not in _kernels:
        _kernels[name] = cp.RawKernel(src, name)
    return _kernels[name]


def if_fire_cuda(potentials: torch.Tensor, threshold: float | torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """CUDA version of ``engine.neurons.if_fire`` for float32 ``[T, C, H, W]`` potentials on the GPU."""
    if not available():
        raise RuntimeError("CuPy + CUDA GPU required")
    if potentials.dtype != torch.float32 or not potentials.is_cuda:
        raise TypeError("potentials must be a float32 CUDA tensor")
    T, C, H, W = potentials.shape
    if T >= NO_SPIKE:
        raise ValueError(f"T must be < {NO_SPIKE}")
    pot = potentials.contiguous()
    theta = torch.as_tensor(threshold, dtype=torch.float32, device=pot.device).expand(C).contiguous()
    times = torch.empty((C, H, W), dtype=torch.uint8, device=pot.device)
    vfire = torch.empty((C, H, W), dtype=torch.float32, device=pot.device)
    n = C * H * W
    block = 256
    with cp.cuda.Stream.from_external(torch.cuda.current_stream(pot.device)):
        _kernel("first_crossing", _FIRST_CROSSING_SRC)(
            ((n + block - 1) // block,), (block,),
            (cp.from_dlpack(pot), cp.from_dlpack(theta), cp.from_dlpack(times), cp.from_dlpack(vfire),
             cp.int32(T), cp.int32(C), cp.int32(H * W)),
        )
    return times, vfire
