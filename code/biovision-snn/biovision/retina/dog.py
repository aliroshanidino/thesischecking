"""Fixed retinal filters: Gaussians, difference-of-Gaussians and divisive normalisation
(CLAUDE.md Section 4.3). The retina emulator is outside the learned network.

Cone approximations (Section 4.2): ``L ~ R``, ``M ~ G``, ``S ~ B``, luminance ``Y = (L + M) / 2``.

* P (Parvo), 4 maps: L/M opponent DoG, centre sigma_c, surround sigma_s = 3 sigma_c:
  ``L+/M-: G_c*L - G_s*M`` and ``M+/L-: G_c*M - G_s*L``, each ON and OFF.
* K (Konio), 2 maps: ``G_k * (S - Y)``, coextensive (centre and surround same size), sigma_k = 2 sigma_c,
  ON and OFF.
* Divisive normalisation (illumination invariance): ``r = max(D, 0) / (eps + G_n * Y)`` for ON and
  ``max(-D, 0) / (eps + G_n * Y)`` for OFF. Multiplying the image by a constant leaves ``r`` unchanged
  (up to ``eps``).

Filtering uses replicate padding so that a uniform image gives exactly zero response, also at the border.
Every function keeps the dtype of its input (float32 in production, float64 in exactness tests).
"""

from __future__ import annotations

import math

import torch
import torch.nn.functional as F


def gaussian_kernel(sigma: float, radius: int | None = None, dtype: torch.dtype = torch.float32) -> torch.Tensor:
    """Normalised 2-D Gaussian ``[2r+1, 2r+1]`` (sums to 1). Default radius ``ceil(3 sigma)``."""
    if sigma <= 0:
        raise ValueError("sigma must be > 0")
    r = int(math.ceil(3 * sigma)) if radius is None else radius
    x = torch.arange(-r, r + 1, dtype=dtype)
    g1 = torch.exp(-(x**2) / (2 * sigma**2))
    g2 = torch.outer(g1, g1)
    return g2 / g2.sum()


def dog_kernel(sigma_c: float, sigma_s: float, dtype: torch.dtype = torch.float32) -> torch.Tensor:
    """Centre-surround DoG ``G_c - G_s`` on a common support set by the surround; sums to ~0."""
    r = int(math.ceil(3 * max(sigma_c, sigma_s)))
    return gaussian_kernel(sigma_c, r, dtype) - gaussian_kernel(sigma_s, r, dtype)


def sdnn_dog_kernel(size: int, sigma_c: float, sigma_s: float, dtype: torch.dtype = torch.float32) -> torch.Tensor:
    """DoG used by Kheradpisheh et al. 2018 / SpykeTorch (Phase 0): ``size x size`` window, zero mean, peak 1.
    ``sigma_c < sigma_s`` gives an ON-centre cell, ``sigma_c > sigma_s`` an OFF-centre cell."""
    r = size // 2
    x = torch.arange(-r, r + 1, dtype=torch.float64)
    d2 = x.view(-1, 1) ** 2 + x.view(1, -1) ** 2
    g = lambda s: torch.exp(-d2 / (2 * s**2)) / (2 * math.pi * s**2)  # noqa: E731
    k = g(sigma_c) - g(sigma_s)
    k = k - k.mean()
    return (k / k.max()).to(dtype)


def sdnn_dog_input(gray: torch.Tensor, kernels: list[torch.Tensor], threshold: float) -> torch.Tensor:
    """Phase 0 retina: filter a ``[H, W]`` grey image (0..255 scale) with each DoG kernel; responses below
    ``threshold`` are silent (a DoG cell fires only above threshold). Returns ``[len(kernels), H, W]`` >= 0."""
    r = torch.stack([filter2d(gray, k) for k in kernels])
    return torch.where(r >= threshold, r, torch.zeros_like(r))


def filter2d(img: torch.Tensor, kernel: torch.Tensor) -> torch.Tensor:
    """Correlate ``img`` (``[H, W]`` or ``[N, H, W]``) with ``kernel`` using replicate padding."""
    squeeze = img.dim() == 2
    x = img.unsqueeze(0) if squeeze else img
    k = kernel.to(device=x.device, dtype=x.dtype)
    r = k.shape[-1] // 2
    x = F.pad(x.unsqueeze(1), (r, r, r, r), mode="replicate")
    y = F.conv2d(x, k.view(1, 1, *k.shape)).squeeze(1)
    return y.squeeze(0) if squeeze else y


def blur(img: torch.Tensor, sigma: float) -> torch.Tensor:
    """Gaussian blur ``G_sigma * img``."""
    return filter2d(img, gaussian_kernel(sigma, dtype=img.dtype))


def cones(rgb: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """``[3, H, W]`` linear RGB -> ``(L, M, S, Y)`` with ``Y = (L + M) / 2``."""
    if rgb.dim() != 3 or rgb.shape[0] != 3:
        raise ValueError(f"expected [3, H, W] RGB, got {tuple(rgb.shape)}")
    L, M, S = rgb[0], rgb[1], rgb[2]
    return L, M, S, (L + M) / 2


def divisive_normalize(D: torch.Tensor, Y: torch.Tensor, sigma_n: float, eps: float) -> tuple[torch.Tensor, torch.Tensor]:
    """``(ON, OFF)`` = ``(max(D,0), max(-D,0)) / (eps + G_n * Y)``."""
    denom = eps + blur(Y, sigma_n)
    return D.clamp(min=0) / denom, (-D).clamp(min=0) / denom


def parvo_konio(
    rgb: torch.Tensor,
    sigma_c: float = 1.0,
    surround_ratio: float = 3.0,
    konio_ratio: float = 2.0,
    sigma_n: float = 3.0,
    eps: float = 1e-3,
) -> torch.Tensor:
    """Normalised responses of the 6 ventral retinal maps for one scale, ``[6, H, W]``.

    Map order: ``P(L+M-) ON, P(L+M-) OFF, P(M+L-) ON, P(M+L-) OFF, K(S-Y) ON, K(S-Y) OFF``.
    ``sigma_n`` is the width of the local mean luminance used for normalisation.
    """
    L, M, S, Y = cones(rgb)
    dt = rgb.dtype
    r = int(math.ceil(3 * sigma_c * surround_ratio))
    g_c = gaussian_kernel(sigma_c, r, dt)
    g_s = gaussian_kernel(sigma_c * surround_ratio, r, dt)
    d_lm = filter2d(L, g_c) - filter2d(M, g_s)
    d_ml = filter2d(M, g_c) - filter2d(L, g_s)
    d_k = blur(S - Y, sigma_c * konio_ratio)
    maps = []
    for D in (d_lm, d_ml, d_k):
        on, off = divisive_normalize(D, Y, sigma_n, eps)
        maps += [on, off]
    return torch.stack(maps)
