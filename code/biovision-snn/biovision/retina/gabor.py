"""Fixed Gabor S1 + C1 front end of Mozafari et al. 2018 (as implemented in SpykeTorch's MozafariShallow), used for
the Phase 0 R-STDP comparison and as the brief's "fixed Gabor S1" ablation (CLAUDE.md Phase 1).

grey image (0..1) -> |Gabor| (4 orientations, 5x5, offset 22.5 deg) -> max pooling (intensities) -> lateral
intensity inhibition (Chebyshev distance 1..r with given factors) -> rank-order latency (all maps ranked together)
-> point-wise inhibition (one orientation per position: earliest spike, ties by intensity).
"""

from __future__ import annotations

import math

import torch
import torch.nn.functional as F

from ..engine.inhibition import feature_wta
from .latency import rank_order


def gabor_kernel(size: int, orientation_deg: float, div: float = 4.0, dtype=torch.float32) -> torch.Tensor:
    """SpykeTorch ``GaborKernel``: wavelength ``2 * size / div``, sigma ``0.8 * lambda``, aspect 0.3; zero mean,
    peak 1."""
    w = size // 2
    x, y = torch.meshgrid(torch.arange(-w, w + 1, dtype=torch.float64), torch.arange(-w, w + 1, dtype=torch.float64),
                          indexing="ij")
    lam = size * 2 / div
    sigma = lam * 0.8
    th = orientation_deg * math.pi / 180
    Y = y * math.cos(th) - x * math.sin(th)
    X = y * math.sin(th) + x * math.cos(th)
    g = torch.exp(-(X * X + 0.09 * Y * Y) / (2 * sigma * sigma)) * torch.cos(2 * math.pi * X / lam)
    g = g - g.mean()
    return (g / g.max()).to(dtype)


def lateral_intensity_inhibition(x: torch.Tensor, percents: list[float]) -> torch.Tensor:
    """``x``: ``[C, H, W]`` intensities. Each cell is strengthened by ``sum_j k(d_ij)`` over the neighbours ``j``
    (Chebyshev distance ``d <= len(percents)``, same map) that are weaker than it, i.e. weaker neighbours fall back
    in the rank order (SpykeTorch ``LateralIntencityInhibition``; zero padding)."""
    r = len(percents)
    size = 2 * r + 1
    d = torch.arange(size, device=x.device) - r
    cheb = torch.maximum(d.abs().view(-1, 1), d.abs().view(1, -1))
    table = torch.tensor([0.0, *percents], device=x.device, dtype=x.dtype)
    k = table[cheb].flatten()                                            # [size*size]
    C, H, W = x.shape
    patches = F.unfold(x.unsqueeze(1), size, padding=r)                   # [C, size*size, H*W]
    center = x.reshape(C, 1, H * W)
    factors = ((center > patches).to(x.dtype) * k.view(1, -1, 1)).sum(1)  # [C, H*W]
    return x * (1 + factors.view(C, H, W))


def gabor_c1(gray01: torch.Tensor, kernels: list[torch.Tensor], pool: tuple[int, int], inhibition: list[float] | None,
             T: int) -> torch.Tensor:
    """``gray01``: ``[H, W]`` in 0..1. Returns C1 spike times ``[len(kernels), H', W']`` (uint8)."""
    k = torch.stack(kernels).unsqueeze(1).to(gray01.device, gray01.dtype)     # [4, 1, s, s]
    s1 = F.conv2d(gray01.view(1, 1, *gray01.shape), k).abs()[0]               # [4, H-s+1, W-s+1]
    c1 = F.max_pool2d(s1.unsqueeze(0), pool[0], pool[1], padding=pool[0] // 2)[0]
    if inhibition:
        c1 = lateral_intensity_inhibition(c1, inhibition)
    times = rank_order(c1, T, theta_in=1e-12, per_channel=False)
    return feature_wta(times, c1)
