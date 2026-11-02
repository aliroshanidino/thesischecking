"""Intensity-to-latency and rank-order coding (CLAUDE.md Section 4.3).

Latency code: ``t = round((T - 1) * (1 - r / r_max))`` where ``r_max`` is the largest response in that
channel (and scale); responses below ``theta_in`` emit no spike. Strong responses fire first, and a
global brightness factor does not change the order because ``r`` is divisively normalised.

Rank code (``coding: rank``): spike time from the sorted order of the supra-threshold responses,
quantised to ``T`` steps.
"""

from __future__ import annotations

import torch

from ..engine.spikes import NO_SPIKE, SPIKE_DTYPE


def intensity_to_latency(r: torch.Tensor, T: int, theta_in: float) -> torch.Tensor:
    """``r``: responses ``[C, H, W]`` (>= 0). Returns uint8 spike times ``[C, H, W]``."""
    if r.dim() != 3:
        raise ValueError(f"expected [C, H, W], got {tuple(r.shape)}")
    r_max = r.amax(dim=(1, 2), keepdim=True)
    active = (r >= theta_in) & (r_max > 0)
    frac = torch.where(r_max > 0, r / r_max.clamp(min=torch.finfo(r.dtype).tiny), torch.zeros_like(r))
    t = torch.floor((T - 1) * (1 - frac) + 0.5).clamp(0, T - 1).to(SPIKE_DTYPE)  # round half up (deterministic)
    return torch.where(active, t, torch.full_like(t, NO_SPIKE))


def rank_order(r: torch.Tensor, T: int, theta_in: float, per_channel: bool = True) -> torch.Tensor:
    """Rank-order code: the ``n`` active responses are sorted (strongest first) and split into ``T`` equal
    groups ("spike packets", Kheradpisheh et al. 2018); group index = spike time.

    ``per_channel=True`` ranks each channel separately; ``False`` ranks all channels together (ON and OFF
    DoG cells compete for the same early packets, as in the paper and SpykeTorch's Intensity2Latency).
    """
    if r.dim() != 3:
        raise ValueError(f"expected [C, H, W], got {tuple(r.shape)}")
    C = r.shape[0] if per_channel else 1
    out = torch.full(r.shape, NO_SPIKE, dtype=SPIKE_DTYPE, device=r.device)
    flat_r = r.reshape(C, -1)
    flat_out = out.view(C, -1)
    for c in range(C):
        idx = torch.nonzero(flat_r[c] >= theta_in).squeeze(1)
        n = idx.numel()
        if n == 0:
            continue
        order = idx[torch.argsort(flat_r[c, idx], descending=True, stable=True)]
        ranks = torch.arange(n, device=r.device)
        flat_out[c, order] = (ranks * T // n).to(SPIKE_DTYPE)
    return out
